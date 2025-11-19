"""
配置管理
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ProviderConfig:
    """提供商配置"""
    provider: str
    api_key: str
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls, provider: str) -> "ProviderConfig":
        """从环境变量创建配置"""
        api_key = None
        extra_params = {}
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if base_url := os.getenv("OPENAI_BASE_URL"):
                extra_params["base_url"] = base_url
                
        elif provider == "azure_openai":
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            extra_params["azure_endpoint"] = os.getenv(
                "AZURE_OPENAI_ENDPOINT",
                ""
            )
            extra_params["api_version"] = os.getenv(
                "AZURE_OPENAI_API_VERSION",
                "2024-02-15-preview"
            )
            
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            
        elif provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError(
                f"未找到 {provider} 的API密钥环境变量"
            )
        
        return cls(
            provider=provider,
            api_key=api_key,
            extra_params=extra_params
        )


@dataclass
class CacheConfig:
    """缓存配置"""
    enabled: bool = True
    ttl_seconds: int = 3600
    max_size: int = 1000
    use_redis: bool = False
    redis_url: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "CacheConfig":
        """从环境变量创建配置"""
        return cls(
            enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600")),
            max_size=int(os.getenv("CACHE_MAX_SIZE", "1000")),
            use_redis=os.getenv("CACHE_USE_REDIS", "false").lower() == "true",
            redis_url=os.getenv("REDIS_URL")
        )


@dataclass
class ClientConfig:
    """客户端配置"""
    provider_config: ProviderConfig
    cache_config: CacheConfig = field(default_factory=CacheConfig)
    
    @classmethod
    def from_env(cls, provider: str) -> "ClientConfig":
        """从环境变量创建配置"""
        return cls(
            provider_config=ProviderConfig.from_env(provider),
            cache_config=CacheConfig.from_env()
        )
    
    def to_client_kwargs(self) -> Dict[str, Any]:
        """转换为客户端初始化参数"""
        return {
            "provider": self.provider_config.provider,
            "api_key": self.provider_config.api_key,
            "enable_cache": self.cache_config.enabled,
            "cache_ttl": self.cache_config.ttl_seconds,
            "cache_max_size": self.cache_config.max_size,
            "use_redis": self.cache_config.use_redis,
            "redis_url": self.cache_config.redis_url,
            **self.provider_config.extra_params
        }
