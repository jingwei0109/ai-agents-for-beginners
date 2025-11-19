"""
GitHub Models 服务提供商实现
"""

import time
from typing import List, AsyncIterator
from openai import AsyncOpenAI, OpenAIError

from ..core import (
    AIProviderBase,
    ModelProvider,
    MessageRole,
    CompletionRequest,
    CompletionResponse,
    ProviderError
)


class GitHubModelsProvider(AIProviderBase):
    """GitHub Models服务提供商"""
    
    def __init__(
        self,
        api_key: str,  # GitHub Personal Access Token
        timeout: int = 60,
        max_retries: int = 3
    ):
        super().__init__(
            api_key=api_key,
            base_url="https://models.inference.ai.azure.com",
            timeout=timeout,
            max_retries=max_retries
        )
        self.provider = ModelProvider.GITHUB_MODELS
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.base_url,
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
            response = await self.client.chat.completions.create(
                model=request.model,
                messages=[msg.to_dict() for msg in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p
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
            raise ProviderError(str(e), self.provider)
    
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
            raise ProviderError(str(e), self.provider)
    
    async def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        # GitHub Models 支持的模型
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4",
            "gpt-3.5-turbo",
            "meta-llama-3-70b-instruct",
            "meta-llama-3-8b-instruct",
            "mistral-large",
            "mistral-small",
            "cohere-command-r-plus",
            "ai21-jamba-instruct"
        ]
    
    async def validate_api_key(self) -> bool:
        """验证API密钥"""
        try:
            await self.client.models.list()
            return True
        except:
            return False
