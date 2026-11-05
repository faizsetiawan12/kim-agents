"""Unique Sentry provider fixes GLM effort projection without changing other profiles."""
from providers import register_provider
from providers.base import ProviderProfile


class SentryGLM(ProviderProfile):
    def build_api_kwargs_extras(self, *, reasoning_config=None, model=None, **context):
        return {}, {'reasoning_effort': 'max'}


def install():
    register_provider(SentryGLM(name='sentry-glm', base_url='https://opencode.ai/zen/go/v1',
                               env_vars=('KIM_SENTRY_GO_KEY',)))
