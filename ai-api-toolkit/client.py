"""
通用AI客户端实现
"""
from typing import List, Optional, Dict, Any, AsyncIterator

try:
    from .base import BaseAIProvider, Message, CompletionResponse
    from .cache import CacheManager, PrefetchManager
    from .providers import (
        OpenAIProvider,
        AzureOpenAIProvider,
        AnthropicProvider,
        GoogleProvider
    )
except ImportError:
    from base import BaseAIProvider, Message, CompletionResponse
    from cache import CacheManager, PrefetchManager
    from providers import (
        OpenAIProvider,
        AzureOpenAIProvider,
        AnthropicProvider,
        GoogleProvider
    )


class AIClient:
    """
    通用AI客户端
    
    支持多个AI提供商，具有缓存和预取功能
    
    示例:
        # OpenAI
        client = AIClient(
            provider="openai",
            api_key="your-api-key"
        )
        
        # Azure OpenAI
        client = AIClient(
            provider="azure_openai",
            api_key="your-api-key",
            azure_endpoint="https://your-resource.openai.azure.com/",
            api_version="2024-02-15-preview"
        )
        
        # Anthropic
        client = AIClient(
            provider="anthropic",
            api_key="your-api-key"
        )
    """
    
    PROVIDER_MAP = {
        "openai": OpenAIProvider,
        "azure_openai": AzureOpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider
    }
    
    def __init__(
        self,
        provider: str,
        api_key: str,
        enable_cache: bool = True,
        cache_ttl: int = 3600,
        cache_max_size: int = 1000,
        use_redis: bool = False,
        redis_url: Optional[str] = None,
        **provider_kwargs
    ):
        """
        初始化AI客户端
        
        Args:
            provider: 提供商名称 (openai, azure_openai, anthropic, google)
            api_key: API密钥
            enable_cache: 是否启用缓存
            cache_ttl: 缓存过期时间（秒）
            cache_max_size: 最大缓存条目数
            use_redis: 是否使用Redis缓存
            redis_url: Redis连接URL
            **provider_kwargs: 提供商特定的参数
        """
        if provider not in self.PROVIDER_MAP:
            raise ValueError(
                f"不支持的提供商: {provider}. "
                f"支持的提供商: {list(self.PROVIDER_MAP.keys())}"
            )
        
        # 初始化提供商
        provider_class = self.PROVIDER_MAP[provider]
        self.provider: BaseAIProvider = provider_class(api_key, **provider_kwargs)
        self.provider.initialize()
        
        # 初始化缓存
        self.cache_manager = CacheManager(
            enabled=enable_cache,
            ttl_seconds=cache_ttl,
            max_size=cache_max_size,
            use_redis=use_redis,
            redis_url=redis_url
        )
        
        # 初始化预取管理器
        self.prefetch_manager = PrefetchManager(self.cache_manager)
        
        # 统计信息
        self._stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_tokens": 0
        }
    
    async def complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
        _skip_cache_write: bool = False,
        **kwargs
    ) -> CompletionResponse:
        """
        生成完成响应
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            use_cache: 是否使用缓存
            **kwargs: 其他参数
            
        Returns:
            CompletionResponse对象
        """
        self._stats["total_requests"] += 1
        
        # 尝试从缓存获取
        cache_key = None
        if use_cache and self.cache_manager.enabled:
            cache_key = self.cache_manager._generate_cache_key(
                messages, model, temperature, **kwargs
            )
            cached_response = self.cache_manager.get(cache_key)
            
            if cached_response:
                self._stats["cache_hits"] += 1
                response = CompletionResponse(**cached_response)
                response.cached = True
                return response
            
            self._stats["cache_misses"] += 1
        
        # 调用提供商API
        response = await self.provider.complete(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # 更新统计
        self._stats["total_tokens"] += response.usage.get("total_tokens", 0)
        
        # 写入缓存
        if use_cache and cache_key and not _skip_cache_write:
            self.cache_manager.set(cache_key, response.to_dict())
        
        return response
    
    async def stream_complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        流式生成完成响应
        
        注意: 流式响应不使用缓存
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Yields:
            生成的文本片段
        """
        self._stats["total_requests"] += 1
        
        async for chunk in self.provider.stream_complete(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            yield chunk
    
    async def prefetch(
        self,
        messages_list: List[List[Message]],
        model: str,
        **kwargs
    ) -> None:
        """
        预取多个请求
        
        Args:
            messages_list: 消息列表的列表
            model: 模型名称
            **kwargs: 其他参数
        """
        await self.prefetch_manager.prefetch(
            self, messages_list, model, **kwargs
        )
    
    def add_to_prefetch_queue(
        self,
        messages: List[Message],
        model: str,
        **kwargs
    ) -> None:
        """
        添加到预取队列
        
        Args:
            messages: 消息列表
            model: 模型名称
            **kwargs: 其他参数
        """
        self.prefetch_manager.add_to_queue(messages, model, **kwargs)
    
    async def process_prefetch_queue(self) -> None:
        """处理预取队列"""
        await self.prefetch_manager.process_queue(self)
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self.cache_manager.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            包含统计信息的字典
        """
        cache_stats = self.cache_manager.get_stats()
        
        return {
            "provider": self.provider.get_provider_name(),
            "total_requests": self._stats["total_requests"],
            "cache_hits": self._stats["cache_hits"],
            "cache_misses": self._stats["cache_misses"],
            "cache_hit_rate": (
                self._stats["cache_hits"] / self._stats["total_requests"]
                if self._stats["total_requests"] > 0 else 0
            ),
            "total_tokens": self._stats["total_tokens"],
            "cache_info": cache_stats
        }
    
    def create_message(
        self,
        role: str,
        content: str,
        name: Optional[str] = None
    ) -> Message:
        """
        创建消息对象
        
        Args:
            role: 角色 (system, user, assistant)
            content: 内容
            name: 名称（可选）
            
        Returns:
            Message对象
        """
        return Message(role=role, content=content, name=name)
    
    def create_messages(
        self,
        *args: tuple[str, str]
    ) -> List[Message]:
        """
        批量创建消息
        
        Args:
            *args: (role, content)元组列表
            
        Returns:
            Message对象列表
            
        示例:
            messages = client.create_messages(
                ("system", "You are a helpful assistant"),
                ("user", "Hello!")
            )
        """
        return [Message(role=role, content=content) for role, content in args]
