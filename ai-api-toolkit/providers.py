"""
各AI提供商的具体实现
"""
from typing import List, Optional, AsyncIterator

try:
    from .base import BaseAIProvider, Message, CompletionResponse
except ImportError:
    from base import BaseAIProvider, Message, CompletionResponse


class OpenAIProvider(BaseAIProvider):
    """OpenAI提供商"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url", None)
        
    def initialize(self) -> None:
        """初始化OpenAI客户端"""
        try:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        except ImportError:
            raise ImportError("请安装openai包: pip install openai")
    
    async def complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResponse:
        """生成完成响应"""
        if not self._client:
            self.initialize()
        
        with self._measure_time() as timer:
            response = await self._client.chat.completions.create(
                model=model,
                messages=[m.to_dict() for m in messages],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        return CompletionResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=response.choices[0].finish_reason,
            provider=self.get_provider_name(),
            latency_ms=timer.elapsed
        )
    
    async def stream_complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成完成响应"""
        if not self._client:
            self.initialize()
        
        stream = await self._client.chat.completions.create(
            model=model,
            messages=[m.to_dict() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_provider_name(self) -> str:
        return "openai"


class AzureOpenAIProvider(BaseAIProvider):
    """Azure OpenAI提供商"""
    
    def __init__(
        self,
        api_key: str,
        azure_endpoint: str,
        api_version: str = "2024-02-15-preview",
        **kwargs
    ):
        super().__init__(api_key, **kwargs)
        self.azure_endpoint = azure_endpoint
        self.api_version = api_version
        
    def initialize(self) -> None:
        """初始化Azure OpenAI客户端"""
        try:
            from openai import AsyncAzureOpenAI
            self._client = AsyncAzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.azure_endpoint,
                api_version=self.api_version
            )
        except ImportError:
            raise ImportError("请安装openai包: pip install openai")
    
    async def complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResponse:
        """生成完成响应"""
        if not self._client:
            self.initialize()
        
        with self._measure_time() as timer:
            response = await self._client.chat.completions.create(
                model=model,
                messages=[m.to_dict() for m in messages],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        return CompletionResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=response.choices[0].finish_reason,
            provider=self.get_provider_name(),
            latency_ms=timer.elapsed
        )
    
    async def stream_complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成完成响应"""
        if not self._client:
            self.initialize()
        
        stream = await self._client.chat.completions.create(
            model=model,
            messages=[m.to_dict() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_provider_name(self) -> str:
        return "azure_openai"


class AnthropicProvider(BaseAIProvider):
    """Anthropic (Claude) 提供商"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        
    def initialize(self) -> None:
        """初始化Anthropic客户端"""
        try:
            from anthropic import AsyncAnthropic
            self._client = AsyncAnthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("请安装anthropic包: pip install anthropic")
    
    async def complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1024,
        **kwargs
    ) -> CompletionResponse:
        """生成完成响应"""
        if not self._client:
            self.initialize()
        
        # Anthropic需要system消息单独处理
        system_message = None
        chat_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                chat_messages.append(msg.to_dict())
        
        with self._measure_time() as timer:
            response = await self._client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=chat_messages,
                **kwargs
            )
        
        return CompletionResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            finish_reason=response.stop_reason,
            provider=self.get_provider_name(),
            latency_ms=timer.elapsed
        )
    
    async def stream_complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1024,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成完成响应"""
        if not self._client:
            self.initialize()
        
        # Anthropic需要system消息单独处理
        system_message = None
        chat_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                chat_messages.append(msg.to_dict())
        
        async with self._client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=chat_messages,
            **kwargs
        ) as stream:
            async for text in stream.text_stream:
                yield text
    
    def get_provider_name(self) -> str:
        return "anthropic"


class GoogleProvider(BaseAIProvider):
    """Google (Gemini) 提供商"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        
    def initialize(self) -> None:
        """初始化Google客户端"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai
        except ImportError:
            raise ImportError("请安装google-generativeai包: pip install google-generativeai")
    
    async def complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResponse:
        """生成完成响应"""
        if not self._client:
            self.initialize()
        
        # 转换消息格式
        gemini_model = self._client.GenerativeModel(model)
        
        # 合并消息为单个prompt（简化处理）
        prompt = "\n".join([f"{m.role}: {m.content}" for m in messages])
        
        with self._measure_time() as timer:
            response = await gemini_model.generate_content_async(
                prompt,
                generation_config=self._client.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
        
        return CompletionResponse(
            content=response.text,
            model=model,
            usage={
                "prompt_tokens": 0,  # Gemini不直接提供token计数
                "completion_tokens": 0,
                "total_tokens": 0
            },
            finish_reason="stop",
            provider=self.get_provider_name(),
            latency_ms=timer.elapsed
        )
    
    async def stream_complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成完成响应"""
        if not self._client:
            self.initialize()
        
        gemini_model = self._client.GenerativeModel(model)
        prompt = "\n".join([f"{m.role}: {m.content}" for m in messages])
        
        response = await gemini_model.generate_content_async(
            prompt,
            generation_config=self._client.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            ),
            stream=True
        )
        
        async for chunk in response:
            if chunk.text:
                yield chunk.text
    
    def get_provider_name(self) -> str:
        return "google"
