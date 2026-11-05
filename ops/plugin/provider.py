"""Unique Ops provider fixes GLM effort projection without changing other profiles."""
from providers import register_provider
from providers.base import ProviderProfile


class OpsGLM(ProviderProfile):
    def build_api_kwargs_extras(self, *, reasoning_config=None, model=None, **context):
        return {}, {'reasoning_effort': 'max'}


def install():
    register_provider(OpsGLM(name='ops-glm', base_url='https://opencode.ai/zen/go/v1',
                               env_vars=('KIM_OPS_GO_KEY',)))
