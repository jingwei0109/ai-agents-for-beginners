"""
AI Provider基类定义
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass
import time


@dataclass
class Message:
    """消息数据类"""
    role: str
    content: str
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class CompletionResponse:
    """完成响应数据类"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    provider: str
    cached: bool = False
    latency_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "finish_reason": self.finish_reason,
            "provider": self.provider,
            "cached": self.cached,
            "latency_ms": self.latency_ms
        }


class BaseAIProvider(ABC):
    """AI提供商基类"""
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        self._client = None
        
    @abstractmethod
    def initialize(self) -> None:
        """初始化客户端"""
        pass
    
    @abstractmethod
    async def complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResponse:
        """生成完成响应"""
        pass
    
    @abstractmethod
    async def stream_complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成完成响应"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """获取提供商名称"""
        pass
    
    def _measure_time(self):
        """时间测量上下文管理器"""
        class Timer:
            def __init__(self):
                self.start = None
                self.elapsed = 0
                
            def __enter__(self):
                self.start = time.time()
                return self
                
            def __exit__(self, *args):
                self.elapsed = (time.time() - self.start) * 1000
                
        return Timer()
