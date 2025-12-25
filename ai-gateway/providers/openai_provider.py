"""
OpenAI 服务提供商实现
"""

import time
import asyncio
from typing import List, AsyncIterator
import httpx
from openai import AsyncOpenAI, OpenAIError

from ..core import (
    AIProviderBase,
    ModelProvider,
    MessageRole,
    CompletionRequest,
    CompletionResponse,
    ProviderError,
    RateLimitError,
    AuthenticationError,
    InvalidRequestError,
    ServiceUnavailableError
)


class OpenAIProvider(AIProviderBase):
    """OpenAI服务提供商"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 60,
        max_retries: int = 3
    ):
        super().__init__(api_key, base_url, timeout, max_retries)
        self.provider = ModelProvider.OPENAI
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries
        )
    
    async def complete(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """执行AI补全"""
        start_time = time.time()
        
        try:
            # 准备请求参数
            params = {
                "model": request.model,
                "messages": [msg.to_dict() for msg in request.messages],
                "temperature": request.temperature,
                "top_p": request.top_p,
                "frequency_penalty": request.frequency_penalty,
                "presence_penalty": request.presence_penalty,
            }
            
            if request.max_tokens:
                params["max_tokens"] = request.max_tokens
            if request.functions:
                params["functions"] = request.functions
            if request.function_call:
                params["function_call"] = request.function_call
            if request.user:
                params["user"] = request.user
            
            # 调用API
            response = await self.client.chat.completions.create(**params)
            
            # 计算延迟
            latency_ms = (time.time() - start_time) * 1000
            
            # 解析响应
            choice = response.choices[0]
            message = choice.message
            
            return CompletionResponse(
                id=response.id,
                model=response.model,
                content=message.content or "",
                role=MessageRole.ASSISTANT,
                finish_reason=choice.finish_reason,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                provider=self.provider,
                latency_ms=latency_ms,
                function_call=message.function_call.model_dump() if message.function_call else None
            )
            
        except OpenAIError as e:
            raise self._convert_error(e)
    
    async def complete_stream(
        self,
        request: CompletionRequest
    ) -> AsyncIterator[str]:
        """执行流式AI补全"""
        try:
            # 准备请求参数
            params = {
                "model": request.model,
                "messages": [msg.to_dict() for msg in request.messages],
                "temperature": request.temperature,
                "stream": True
            }
            
            if request.max_tokens:
                params["max_tokens"] = request.max_tokens
            
            # 流式调用
            stream = await self.client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
                        
        except OpenAIError as e:
            raise self._convert_error(e)
    
    async def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data]
        except OpenAIError as e:
            raise self._convert_error(e)
    
    async def validate_api_key(self) -> bool:
        """验证API密钥"""
        try:
            await self.client.models.list()
            return True
        except OpenAIError:
            return False
    
    def _convert_error(self, error: OpenAIError) -> ProviderError:
        """转换OpenAI错误为统一错误类型"""
        error_message = str(error)
        
        if "rate_limit" in error_message.lower():
            return RateLimitError(
                error_message,
                self.provider,
                status_code=429
            )
        elif "authentication" in error_message.lower() or "api_key" in error_message.lower():
            return AuthenticationError(
                error_message,
                self.provider,
                status_code=401
            )
        elif "invalid" in error_message.lower():
            return InvalidRequestError(
                error_message,
                self.provider,
                status_code=400
            )
        elif "service" in error_message.lower() or "unavailable" in error_message.lower():
            return ServiceUnavailableError(
                error_message,
                self.provider,
                status_code=503
            )
        else:
            return ProviderError(
                error_message,
                self.provider
            )
