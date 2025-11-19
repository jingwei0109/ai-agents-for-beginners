"""
Azure OpenAI 服务提供商实现
"""

import time
from typing import List, AsyncIterator, Optional
from openai import AsyncAzureOpenAI, OpenAIError

from ..core import (
    AIProviderBase,
    ModelProvider,
    MessageRole,
    CompletionRequest,
    CompletionResponse,
    ProviderError,
    RateLimitError,
    AuthenticationError
)


class AzureOpenAIProvider(AIProviderBase):
    """Azure OpenAI服务提供商"""
    
    def __init__(
        self,
        api_key: str,
        azure_endpoint: str,
        api_version: str = "2024-05-01-preview",
        timeout: int = 60,
        max_retries: int = 3
    ):
        super().__init__(api_key, azure_endpoint, timeout, max_retries)
        self.provider = ModelProvider.AZURE_OPENAI
        self.api_version = api_version
        
        self.client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
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
            # 对于Azure，model参数实际上是deployment name
            response = await self.client.chat.completions.create(
                model=request.model,  # deployment name
                messages=[msg.to_dict() for msg in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                frequency_penalty=request.frequency_penalty,
                presence_penalty=request.presence_penalty
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
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
                latency_ms=latency_ms
            )
            
        except OpenAIError as e:
            raise self._convert_error(e)
    
    async def complete_stream(
        self,
        request: CompletionRequest
    ) -> AsyncIterator[str]:
        """执行流式AI补全"""
        try:
            stream = await self.client.chat.completions.create(
                model=request.model,
                messages=[msg.to_dict() for msg in request.messages],
                temperature=request.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
                        
        except OpenAIError as e:
            raise self._convert_error(e)
    
    async def get_available_models(self) -> List[str]:
        """获取可用模型列表（Azure中是deployments）"""
        # Azure OpenAI需要通过REST API获取deployments
        # 这里返回常见的模型名称
        return [
            "gpt-4",
            "gpt-4-32k",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-35-turbo",
            "gpt-35-turbo-16k"
        ]
    
    async def validate_api_key(self) -> bool:
        """验证API密钥"""
        try:
            # 尝试进行一个简单的调用
            await self.client.chat.completions.create(
                model="gpt-35-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except:
            return False
    
    def _convert_error(self, error: OpenAIError) -> ProviderError:
        """转换错误"""
        error_message = str(error)
        
        if "rate" in error_message.lower():
            return RateLimitError(error_message, self.provider)
        elif "auth" in error_message.lower():
            return AuthenticationError(error_message, self.provider)
        else:
            return ProviderError(error_message, self.provider)
