"""
AI Gateway - 通用AI接口预取接入工具

一个企业级的AI接口网关,提供:
- 统一接口：支持多个AI服务提供商
- 智能缓存：减少重复请求,降低成本
- 负载均衡：分散请求到多个提供商
- 自动重试：失败时自动重试
- Fallback：主提供商失败时切换到备用
- 速率限制：防止超出API限额
"""

from .gateway import AIGateway, ProviderConfig
from .core import (
    AIProviderBase,
    ModelProvider,
    MessageRole,
    Message,
    CompletionRequest,
    CompletionResponse,
    ProviderError
)
from .providers import (
    OpenAIProvider,
    AzureOpenAIProvider,
    GitHubModelsProvider
)
from .cache import CacheManager, MemoryCacheBackend

__version__ = "1.0.0"

__all__ = [
    'AIGateway',
    'ProviderConfig',
    'AIProviderBase',
    'ModelProvider',
    'MessageRole',
    'Message',
    'CompletionRequest',
    'CompletionResponse',
    'ProviderError',
    'OpenAIProvider',
    'AzureOpenAIProvider',
    'GitHubModelsProvider',
    'CacheManager',
    'MemoryCacheBackend'
]
