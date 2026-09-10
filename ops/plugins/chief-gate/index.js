"use strict";

const { definePluginEntry } = require("openclaw/plugin-sdk/plugin-entry");
const fs = require("fs");
const path = require("path");

const GATE_LOG = "/tmp/openclaw/chief-gate.log";
const ENGINEER_SESSIONS_DIR = "/home/faiz/.openclaw/agents/engineer/sessions";
const CHIEF_TOPIC_ID = "1";
const ENGINEER_TOPIC_ID = "59";
const QUANT_TOPIC_ID = "62";

function log(msg) {
  const ts = new Date().toISOString();
  const line = `[${ts}] ${msg}\n`;
  try {
    fs.appendFileSync(GATE_LOG, line);
  } catch {}
}

module.exports = definePluginEntry({
  id: "chief-gate",
  name: "Chief Gate",
  description:
    "Requires KIM Engineer Bot to file TASK COMPLETE with Chief before final " +
    "completion summaries, while allowing alerts and approval requests.",

  register(api) {
    api.on("before_agent_finalize", async (event, ctx) => {
      log(
        `FINALIZE: agent=${ctx.agentId} key=${ctx.sessionKey} ` +
          `stop=${event.stopHookActive} tx=${!!event.transcriptPath}`
      );

      if (ctx.agentId !== "engineer") return;
      if (!isEngineerTopic(ctx.sessionKey)) return;
      if (event.stopHookActive) return;

      const transcriptPath = event.transcriptPath;
      if (!transcriptPath) {
        log("FINALIZE: no transcriptPath, allowing");
        return;
      }

      const audit = auditTranscriptFiles([transcriptPath]);
      if (!audit.requiresChiefReport) {
        log("FINALIZE: BYPASS — not a final completion summary");
        return;
      }

      if (!audit.sessionReported) {
        log("FINALIZE: BLOCKED — completion summary without TASK COMPLETE");
        return reviseInstruction();
      }

      log("FINALIZE: APPROVED — TASK COMPLETE report found");
      return;
    });

    api.on("message_sending", async (event, ctx) => {
      const preview = String(event.content || "").slice(0, 80);
      log(
        `MSG_SENDING: agent=${ctx.agentId} key=${ctx.sessionKey} ` +
          `threadId=${event.threadId} preview=${preview}`
      );

      const laneViolation = validateAgentTopic(ctx.agentId, event.threadId);
      if (laneViolation) {
        log(`MSG_SENDING: BLOCKED — ${laneViolation}`);
        return {
          cancel: true,
          content: "Message blocked by KIM topic-lane policy.",
        };
      }

      if (ctx.agentId !== "engineer") return;
      if (String(event.threadId) !== ENGINEER_TOPIC_ID) return;

      const text = String(event.content || "");
      if (!requiresChiefReport(text)) {
        log("MSG_SENDING: BYPASS — alert/status/approval/redirect");
        return;
      }

      const files = transcriptFilesForSession(ctx.sessionKey);
      const audit = auditTranscriptFiles(files);
      if (!audit.sessionReported) {
        log("MSG_SENDING: BLOCKED — completion summary without TASK COMPLETE");
        return {
          cancel: true,
          content:
            "Chief Gate blocked this completion summary. File TASK COMPLETE " +
            "with Chief first, or rewrite as an alert, approval request, " +
            "blocked report, redirect, or interim diagnostic status.",
        };
      }

      log("MSG_SENDING: APPROVED — TASK COMPLETE report found");
      return;
    });

    log("Registered chief-gate for engineer final completion summaries.");
  },
});

function isEngineerTopic(sessionKey) {
  return String(sessionKey || "").includes(`topic:${ENGINEER_TOPIC_ID}`);
}

function validateAgentTopic(agentId, threadId) {
  const topicId = String(threadId ?? "");

  if (agentId === "chief" && topicId !== CHIEF_TOPIC_ID) {
    return `chief attempted topic ${topicId || "none"}`;
  }

  if (
    agentId === "engineer" &&
    topicId !== ENGINEER_TOPIC_ID &&
    topicId !== CHIEF_TOPIC_ID
  ) {
    return `engineer attempted topic ${topicId || "none"}`;
  }

  if (agentId === "quant" && topicId !== QUANT_TOPIC_ID) {
    return `quant attempted topic ${topicId || "none"}`;
  }

  return null;
}

function transcriptFilesForSession(sessionKey) {
  if (!sessionKey) return [];

  let sessionId = null;
  try {
    const sessionsPath = path.join(ENGINEER_SESSIONS_DIR, "sessions.json");
    const sessionsJson = JSON.parse(fs.readFileSync(sessionsPath, "utf-8"));
    const entry = sessionsJson[sessionKey];
    sessionId = typeof entry === "string" ? entry : entry?.sessionId;
  } catch (err) {
    log(`TRANSCRIPT: failed to read sessions.json: ${err.message}`);
  }

  if (!sessionId) return [];

  try {
    return fs
      .readdirSync(ENGINEER_SESSIONS_DIR)
      .filter((name) => name.startsWith(sessionId) && name.endsWith(".jsonl"))
      .map((name) => path.join(ENGINEER_SESSIONS_DIR, name));
  } catch (err) {
    log(`TRANSCRIPT: failed to list session files: ${err.message}`);
    return [];
  }
}

function auditTranscriptFiles(files) {
  let sessionReported = false;
  let finalResponseText = "";

  for (const file of files) {
    try {
      const raw = fs.readFileSync(file, "utf-8");
      const lines = raw.trim().split("\n");
      for (const line of lines) {
        try {
          const entry = JSON.parse(line);
          if (entry.type !== "message") continue;
          const content = entry.message?.content;
          if (!Array.isArray(content)) continue;

          if (entry.message?.role === "assistant") {
            for (const block of content) {
              if (block.type === "text" && typeof block.text === "string") {
                finalResponseText = block.text;
              }
            }
          }

          for (const block of content) {
            if (block.type !== "toolCall") continue;
            if (block.name !== "sessions_send") continue;
            const msg = block.arguments?.message || "";
            const target = block.arguments?.sessionKey || "";
            if (msg.includes("TASK COMPLETE") && target.includes("agent:main")) {
              sessionReported = true;
            }
          }
        } catch {}
      }
    } catch (err) {
      log(`TRANSCRIPT: failed to read ${file}: ${err.message}`);
    }
  }

  return {
    sessionReported,
    requiresChiefReport: requiresChiefReport(finalResponseText),
  };
}

function requiresChiefReport(text) {
  const normalized = String(text || "").trim().toLowerCase();
  if (!normalized) return false;

  const bypassPrefixes = [
    "critical",
    "alert",
    "approval needed",
    "approval required",
    "blocked",
    "cannot proceed",
    "unable to proceed",
    "route this through chief",
    "diagnostic",
    "status",
  ];

  if (bypassPrefixes.some((prefix) => normalized.startsWith(prefix))) {
    return false;
  }

  const completionSignals = [
    "task complete",
    "fixed",
    "completed",
    "done",
    "resolved",
    "deployed",
    "committed",
  ];

  return completionSignals.some((signal) => normalized.includes(signal));
}

function reviseInstruction() {
  return {
    action: "revise",
    reason:
      "Chief Gate: final completion summaries require a TASK COMPLETE report to Chief Bot first.",
    retry: {
      instruction:
        "If this is a final completion summary for executed work, first call " +
        "sessions_send with a TASK COMPLETE report to Chief. If this is an alert, " +
        "approval request, inability-to-proceed report, redirect, or interim " +
        "diagnostic status, rewrite it with the appropriate status prefix instead " +
        "of a completion claim.",
      maxAttempts: 3,
    },
  };
}
