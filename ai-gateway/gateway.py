"""
AI Gateway - 统一的AI接口网关
提供统一接口、缓存、负载均衡、重试、fallback等功能
"""

import asyncio
import time
from typing import List, Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass
import random

from .core import (
    AIProviderBase,
    ModelProvider,
    Message,
    MessageRole,
    CompletionRequest,
    CompletionResponse,
    ProviderError,
    RateLimitError,
    ServiceUnavailableError
)
from .cache import CacheManager
from .providers import (
    OpenAIProvider,
    AzureOpenAIProvider,
    GitHubModelsProvider
)


@dataclass
class ProviderConfig:
    """服务提供商配置"""
    provider: AIProviderBase
    weight: int = 1  # 负载均衡权重
    priority: int = 1  # 优先级（数字越小优先级越高）
    enabled: bool = True
    max_requests_per_minute: int = 0  # 0表示无限制


class AIGateway:
    """
    AI接口网关
    
    功能:
    - 统一接口：支持多个AI服务提供商
    - 智能缓存：减少重复请求
    - 负载均衡：分散请求到多个提供商
    - 自动重试：失败时自动重试
    - Fallback：主提供商失败时切换到备用提供商
    - 速率限制：防止超出API限额
    """
    
    def __init__(
        self,
        cache_manager: Optional[CacheManager] = None,
        enable_cache: bool = True,
        enable_retry: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.providers: Dict[str, ProviderConfig] = {}
        self.cache_manager = cache_manager or CacheManager()
        self.enable_cache = enable_cache
        self.enable_retry = enable_retry
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # 统计信息
        self._stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "provider_requests": {},
            "errors": {}
        }
    
    def add_provider(
        self,
        name: str,
        provider: AIProviderBase,
        weight: int = 1,
        priority: int = 1,
        enabled: bool = True
    ) -> None:
        """
        添加服务提供商
        
        Args:
            name: 提供商名称
            provider: 提供商实例
            weight: 负载均衡权重
            priority: 优先级（越小越高）
            enabled: 是否启用
        """
        self.providers[name] = ProviderConfig(
            provider=provider,
            weight=weight,
            priority=priority,
            enabled=enabled
        )
        self._stats["provider_requests"][name] = 0
        self._stats["errors"][name] = 0
    
    def remove_provider(self, name: str) -> None:
        """移除服务提供商"""
        if name in self.providers:
            del self.providers[name]
    
    def enable_provider(self, name: str) -> None:
        """启用服务提供商"""
        if name in self.providers:
            self.providers[name].enabled = True
    
    def disable_provider(self, name: str) -> None:
        """禁用服务提供商"""
        if name in self.providers:
            self.providers[name].enabled = False
    
    def _select_provider(self) -> Optional[str]:
        """
        选择服务提供商
        使用加权随机选择 + 优先级
        """
        enabled_providers = [
            (name, config) for name, config in self.providers.items()
            if config.enabled
        ]
        
        if not enabled_providers:
            return None
        
        # 按优先级排序
        enabled_providers.sort(key=lambda x: x[1].priority)
        
        # 只选择最高优先级的提供商
        top_priority = enabled_providers[0][1].priority
        top_providers = [
            (name, config) for name, config in enabled_providers
            if config.priority == top_priority
        ]
        
        # 加权随机选择
        weights = [config.weight for _, config in top_providers]
        selected = random.choices(top_providers, weights=weights)[0]
        
        return selected[0]
    
    async def complete(
        self,
        messages: List[Message] | List[Dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        provider_name: Optional[str] = None,
        use_cache: bool = True
    ) -> CompletionResponse:
        """
        执行AI补全
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            provider_name: 指定使用的提供商名称（可选）
            use_cache: 是否使用缓存
            
        Returns:
            补全响应
        """
        self._stats["total_requests"] += 1
        
        # 转换消息格式
        if messages and isinstance(messages[0], dict):
            messages = [
                Message(
                    role=MessageRole(msg["role"]),
                    content=msg["content"]
                )
                for msg in messages
            ]
        
        # 尝试从缓存获取
        if use_cache and self.enable_cache:
            cached_response = await self.cache_manager.get(
                messages=[msg.to_dict() for msg in messages],
                model=model,
                temperature=temperature
            )
            
            if cached_response:
                self._stats["cache_hits"] += 1
                cached_response.cached = True
                return cached_response
        
        self._stats["cache_misses"] += 1
        
        # 创建请求
        request = CompletionRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 选择或使用指定的提供商
        if provider_name and provider_name in self.providers:
            selected_provider = provider_name
        else:
            selected_provider = self._select_provider()
        
        if not selected_provider:
            raise ProviderError(
                "No enabled providers available",
                ModelProvider.CUSTOM
            )
        
        # 尝试执行请求
        last_error = None
        attempts = 0
        
        while attempts < self.max_retries:
            try:
                provider_config = self.providers[selected_provider]
                provider = provider_config.provider
                
                # 执行请求
                response = await provider.complete(request)
                
                # 更新统计
                self._stats["provider_requests"][selected_provider] += 1
                
                # 缓存响应
                if use_cache and self.enable_cache:
                    await self.cache_manager.set(
                        messages=[msg.to_dict() for msg in messages],
                        model=model,
                        response=response,
                        temperature=temperature
                    )
                
                return response
                
            except (RateLimitError, ServiceUnavailableError) as e:
                last_error = e
                self._stats["errors"][selected_provider] += 1
                
                # 尝试切换到其他提供商
                self.providers[selected_provider].enabled = False
                new_provider = self._select_provider()
                
                if new_provider:
                    selected_provider = new_provider
                    attempts += 1
                    await asyncio.sleep(self.retry_delay * attempts)
                else:
                    # 没有可用的提供商了
                    break
                    
            except Exception as e:
                last_error = e
                self._stats["errors"][selected_provider] += 1
                
                if not self.enable_retry:
                    raise
                
                attempts += 1
                if attempts < self.max_retries:
                    await asyncio.sleep(self.retry_delay * attempts)
                else:
                    break
        
        # 所有尝试都失败了
        if last_error:
            raise last_error
        else:
            raise ProviderError(
                "All retry attempts failed",
                ModelProvider.CUSTOM
            )
    
    async def complete_stream(
        self,
        messages: List[Message] | List[Dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        provider_name: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        执行流式AI补全
        注意：流式调用不使用缓存
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            provider_name: 指定使用的提供商名称（可选）
            
        Yields:
            响应文本片段
        """
        # 转换消息格式
        if messages and isinstance(messages[0], dict):
            messages = [
                Message(
                    role=MessageRole(msg["role"]),
                    content=msg["content"]
                )
                for msg in messages
            ]
        
        # 创建请求
        request = CompletionRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        # 选择提供商
        if provider_name and provider_name in self.providers:
            selected_provider = provider_name
        else:
            selected_provider = self._select_provider()
        
        if not selected_provider:
            raise ProviderError(
                "No enabled providers available",
                ModelProvider.CUSTOM
            )
        
        provider = self.providers[selected_provider].provider
        
        # 流式输出
        async for chunk in provider.complete_stream(request):
            yield chunk
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        cache_stats = await self.cache_manager.get_stats()
        
        return {
            "gateway": self._stats,
            "cache": cache_stats,
            "providers": {
                name: {
                    "enabled": config.enabled,
                    "weight": config.weight,
                    "priority": config.priority
                }
                for name, config in self.providers.items()
            }
        }
    
    async def health_check(self) -> Dict[str, bool]:
        """
        健康检查
        检查所有提供商的API密钥是否有效
        """
        results = {}
        
        for name, config in self.providers.items():
            try:
                is_valid = await config.provider.validate_api_key()
                results[name] = is_valid
            except Exception:
                results[name] = False
        
        return results
