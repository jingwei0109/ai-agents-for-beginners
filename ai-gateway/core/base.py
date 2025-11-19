"""
AI接口基础抽象类
定义统一的接口规范
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass
from enum import Enum


class ModelProvider(str, Enum):
    """AI服务提供商枚举"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    GITHUB_MODELS = "github_models"
    GOOGLE_GEMINI = "google_gemini"
    CUSTOM = "custom"


class MessageRole(str, Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


@dataclass
class Message:
    """消息数据结构"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = {
            "role": self.role.value,
            "content": self.content
        }
        if self.name:
            data["name"] = self.name
        if self.function_call:
            data["function_call"] = self.function_call
        return data


@dataclass
class CompletionRequest:
    """AI补全请求"""
    messages: List[Message]
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stream: bool = False
    functions: Optional[List[Dict]] = None
    function_call: Optional[str] = None
    user: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = {
            "messages": [msg.to_dict() for msg in self.messages],
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stream": self.stream
        }
        
        if self.max_tokens:
            data["max_tokens"] = self.max_tokens
        if self.functions:
            data["functions"] = self.functions
        if self.function_call:
            data["function_call"] = self.function_call
        if self.user:
            data["user"] = self.user
            
        return data


@dataclass
class CompletionResponse:
    """AI补全响应"""
    id: str
    model: str
    content: str
    role: MessageRole
    finish_reason: str
    usage: Dict[str, int]
    provider: ModelProvider
    latency_ms: float
    cached: bool = False
    function_call: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "model": self.model,
            "content": self.content,
            "role": self.role.value,
            "finish_reason": self.finish_reason,
            "usage": self.usage,
            "provider": self.provider.value,
            "latency_ms": self.latency_ms,
            "cached": self.cached,
            "function_call": self.function_call
        }


class AIProviderBase(ABC):
    """AI服务提供商基类"""
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.provider = ModelProvider.CUSTOM
    
    @abstractmethod
    async def complete(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """
        执行AI补全
        
        Args:
            request: 补全请求
            
        Returns:
            补全响应
        """
        pass
    
    @abstractmethod
    async def complete_stream(
        self,
        request: CompletionRequest
    ) -> AsyncIterator[str]:
        """
        执行流式AI补全
        
        Args:
            request: 补全请求
            
        Yields:
            响应文本片段
        """
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """
        获取可用模型列表
        
        Returns:
            模型名称列表
        """
        pass
    
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """
        验证API密钥是否有效
        
        Returns:
            是否有效
        """
        pass
    
    def _create_messages_from_list(
        self,
        messages: List[Dict]
    ) -> List[Message]:
        """从字典列表创建Message对象"""
        return [
            Message(
                role=MessageRole(msg["role"]),
                content=msg["content"],
                name=msg.get("name"),
                function_call=msg.get("function_call")
            )
            for msg in messages
        ]


class ProviderError(Exception):
    """服务提供商错误"""
    def __init__(
        self,
        message: str,
        provider: ModelProvider,
        status_code: Optional[int] = None,
        retry_after: Optional[int] = None
    ):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code
        self.retry_after = retry_after


class RateLimitError(ProviderError):
    """速率限制错误"""
    pass


class AuthenticationError(ProviderError):
    """认证错误"""
    pass


class InvalidRequestError(ProviderError):
    """无效请求错误"""
    pass


class ServiceUnavailableError(ProviderError):
    """服务不可用错误"""
    pass
