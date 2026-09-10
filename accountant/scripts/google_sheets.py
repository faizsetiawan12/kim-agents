"""Google Sheets API client using stdlib only. No external packages needed."""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

KEY_FILE_ENV = "KIM_GOOGLE_SHEETS_KEY_FILE"
SCOPES = "https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive"


def _load_dotenv(path: str | Path = ".env") -> None:
    # ponytail: 5-line parser, upgrade to python-dotenv if quoting/multiline needed
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def _b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


def _key_file() -> Path:
    val = os.environ.get(KEY_FILE_ENV)
    assert val, f"{KEY_FILE_ENV} is not set"  # fail fast, no silent default
    return Path(val)


def _load_service_account() -> dict[str, Any]:
    with open(_key_file(), "r", encoding="utf-8") as f:
        return json.load(f)


def _sign_rs256(data: bytes, pem_key: str) -> bytes:
    """Sign SHA256 with RSA private key via OpenSSL CLI (zero-dep fallback)."""
    import os
    import subprocess
    import tempfile

    key_fd, key_path = tempfile.mkstemp(prefix="sa-key-", suffix=".pem")
    try:
        with os.fdopen(key_fd, "w", encoding="utf-8") as f:
            f.write(pem_key)
        os.chmod(key_path, 0o600)
        proc = subprocess.Popen(
            ["openssl", "dgst", "-sha256", "-sign", key_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate(input=data)
        if proc.returncode != 0:
            raise RuntimeError(f"openssl sign failed: {stderr.decode('utf-8', 'replace')}")
        return stdout
    finally:
        if os.path.exists(key_path):
            try:
                os.remove(key_path)
            except OSError:
                pass


def get_access_token() -> str:
    """Exchange service-account JWT for an access token."""
    info = _load_service_account()
    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {
        "iss": info["client_email"],
        "scope": SCOPES,
        "aud": "https://oauth2.googleapis.com/token",
        "exp": now + 3600,
        "iat": now,
    }
    signing_input = (
        _b64url(json.dumps(header).encode("utf-8"))
        + "."
        + _b64url(json.dumps(payload).encode("utf-8"))
    )
    signature = _sign_rs256(signing_input.encode("ascii"), info["private_key"])
    assertion = signing_input + "." + _b64url(signature)

    req_body = urllib.parse.urlencode(
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }
    ).encode("ascii")

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=req_body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["access_token"]


def create_rdn_book() -> tuple[str, str]:
    """Create a new Google Sheet with 3 tabs and standard bookkeeping headers."""
    token = get_access_token()
    headers_list = [
        "date_wib",
        "who_pasted",
        "type",
        "owner",
        "amount_rp",
        "proof_text",
        "oscar_approved",
        "note",
    ]

    body = {
        "properties": {"title": "KIM RDN Profit-Share Book"},
        "sheets": [
            {
                "properties": {"title": "Journal"},
                "data": [
                    {
                        "startRow": 0,
                        "startColumn": 0,
                        "rowData": [
                            {
                                "values": [
                                    {"userEnteredValue": {"stringValue": h}}
                                    for h in headers_list
                                ]
                            }
                        ],
                    }
                ],
            },
            {
                "properties": {"title": "Ledger"},
                "data": [
                    {
                        "startRow": 0,
                        "startColumn": 0,
                        "rowData": [
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Owner / Account"
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Current Balance (Rp)"
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Last Updated"
                                        }
                                    },
                                ]
                            }
                        ],
                    }
                ],
            },
            {
                "properties": {"title": "ProfitShare"},
                "data": [
                    {
                        "startRow": 0,
                        "startColumn": 0,
                        "rowData": [
                            {
                                "values": [
                                    {"userEnteredValue": {"stringValue": "Owner"}},
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Realized Profit (Rp)"
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Fee to Wahyu (5%)"
                                        }
                                    },
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Net Profit (Rp)"
                                        }
                                    },
                                ]
                            }
                        ],
                    }
                ],
            },
        ],
    }

    req = urllib.request.Request(
        "https://sheets.googleapis.com/v4/spreadsheets",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        sheet_id = res["spreadsheetId"]
        sheet_url = res["spreadsheetUrl"]
        return sheet_id, sheet_url


if __name__ == "__main__":
    _load_dotenv()
    sid, surl = create_rdn_book()
    print(f"SHEET_ID={sid}")
    print(f"SHEET_URL={surl}")
