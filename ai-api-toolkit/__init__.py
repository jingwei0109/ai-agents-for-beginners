"""
通用AI接口预取接入工具
支持多个AI服务提供商，具有缓存和预取功能
"""

from .client import AIClient
from .cache import CacheManager
from .providers import OpenAIProvider, AzureOpenAIProvider, AnthropicProvider

__version__ = "1.0.0"
__all__ = [
    "AIClient",
    "CacheManager", 
    "OpenAIProvider",
    "AzureOpenAIProvider",
    "AnthropicProvider"
]
