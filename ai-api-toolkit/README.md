# AI API Toolkit - 通用AI接口预取接入工具

一个强大的通用AI接口工具，支持多个AI服务提供商，具有缓存和预取功能。

## 特性

- 🔌 **多提供商支持**: OpenAI、Azure OpenAI、Anthropic (Claude)、Google (Gemini)
- 💾 **智能缓存**: 支持内存缓存和Redis缓存，自动LRU淘汰
- ⚡ **预取功能**: 批量预取请求，提高响应速度
- 📊 **统计分析**: 详细的请求和缓存统计信息
- 🔄 **流式响应**: 支持流式输出
- 🛠️ **易于配置**: 支持环境变量和代码配置

## 安装

```bash
pip install openai anthropic google-generativeai redis
```

可选依赖：
- `redis`: Redis缓存支持
- `anthropic`: Anthropic/Claude支持
- `google-generativeai`: Google Gemini支持

## 快速开始

### 1. OpenAI

```python
import asyncio
from ai_api_toolkit import AIClient, Message

async def main():
    # 创建客户端
    client = AIClient(
        provider="openai",
        api_key="your-openai-api-key",
        enable_cache=True
    )
    
    # 创建消息
    messages = [
        Message(role="system", content="You are a helpful assistant"),
        Message(role="user", content="What is Python?")
    ]
    
    # 生成响应
    response = await client.complete(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    print(f"响应: {response.content}")
    print(f"使用token: {response.usage['total_tokens']}")
    print(f"延迟: {response.latency_ms:.2f}ms")
    print(f"来自缓存: {response.cached}")
    
    # 查看统计
    stats = client.get_stats()
    print(f"统计: {stats}")

asyncio.run(main())
```

### 2. Azure OpenAI

```python
client = AIClient(
    provider="azure_openai",
    api_key="your-azure-api-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_version="2024-02-15-preview"
)
```

### 3. Anthropic (Claude)

```python
client = AIClient(
    provider="anthropic",
    api_key="your-anthropic-api-key"
)

response = await client.complete(
    messages=messages,
    model="claude-3-5-sonnet-20241022"
)
```

### 4. Google (Gemini)

```python
client = AIClient(
    provider="google",
    api_key="your-google-api-key"
)

response = await client.complete(
    messages=messages,
    model="gemini-pro"
)
```

## 高级功能

### 流式响应

```python
async for chunk in client.stream_complete(
    messages=messages,
    model="gpt-4o-mini"
):
    print(chunk, end="", flush=True)
```

### 预取功能

```python
# 批量预取
messages_list = [
    [Message(role="user", content="What is AI?")],
    [Message(role="user", content="What is ML?")],
    [Message(role="user", content="What is DL?")]
]

await client.prefetch(
    messages_list=messages_list,
    model="gpt-4o-mini"
)

# 后续请求将直接从缓存获取
response = await client.complete(
    messages=messages_list[0],
    model="gpt-4o-mini"
)
```

### 预取队列

```python
# 添加到队列
client.add_to_prefetch_queue(messages1, model="gpt-4o-mini")
client.add_to_prefetch_queue(messages2, model="gpt-4o-mini")

# 处理队列
await client.process_prefetch_queue()
```

### Redis缓存

```python
client = AIClient(
    provider="openai",
    api_key="your-api-key",
    enable_cache=True,
    use_redis=True,
    redis_url="redis://localhost:6379/0"
)
```

### 从环境变量配置

```python
from ai_api_toolkit.config import ClientConfig

# 设置环境变量
# export OPENAI_API_KEY=your-key
# export CACHE_ENABLED=true
# export CACHE_TTL_SECONDS=7200

config = ClientConfig.from_env("openai")
client = AIClient(**config.to_client_kwargs())
```

## 环境变量

### 提供商配置

- `OPENAI_API_KEY`: OpenAI API密钥
- `OPENAI_BASE_URL`: OpenAI基础URL（可选）
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API密钥
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI端点
- `AZURE_OPENAI_API_VERSION`: Azure OpenAI API版本
- `ANTHROPIC_API_KEY`: Anthropic API密钥
- `GOOGLE_API_KEY`: Google API密钥

### 缓存配置

- `CACHE_ENABLED`: 是否启用缓存（默认: true）
- `CACHE_TTL_SECONDS`: 缓存过期时间（默认: 3600）
- `CACHE_MAX_SIZE`: 最大缓存条目数（默认: 1000）
- `CACHE_USE_REDIS`: 是否使用Redis（默认: false）
- `REDIS_URL`: Redis连接URL

## API参考

### AIClient

主客户端类。

**初始化参数**:
- `provider` (str): 提供商名称
- `api_key` (str): API密钥
- `enable_cache` (bool): 是否启用缓存
- `cache_ttl` (int): 缓存过期时间（秒）
- `cache_max_size` (int): 最大缓存条目数
- `use_redis` (bool): 是否使用Redis
- `redis_url` (str): Redis连接URL

**方法**:
- `complete()`: 生成完成响应
- `stream_complete()`: 流式生成响应
- `prefetch()`: 批量预取
- `add_to_prefetch_queue()`: 添加到预取队列
- `process_prefetch_queue()`: 处理预取队列
- `clear_cache()`: 清空缓存
- `get_stats()`: 获取统计信息

### Message

消息数据类。

**属性**:
- `role` (str): 角色 (system, user, assistant)
- `content` (str): 内容
- `name` (str, optional): 名称

### CompletionResponse

响应数据类。

**属性**:
- `content` (str): 生成的内容
- `model` (str): 使用的模型
- `usage` (dict): Token使用情况
- `finish_reason` (str): 完成原因
- `provider` (str): 提供商名称
- `cached` (bool): 是否来自缓存
- `latency_ms` (float): 延迟（毫秒）

## 最佳实践

1. **启用缓存**: 对于重复的请求，缓存可以显著提高响应速度
2. **使用预取**: 如果能预测用户需求，可以使用预取功能提前准备响应
3. **Redis缓存**: 在生产环境或多实例部署时使用Redis
4. **监控统计**: 定期检查统计信息，优化缓存策略
5. **流式响应**: 对于长文本生成，使用流式响应提升用户体验

## 许可证

MIT License

## 贡献

欢迎贡献！请提交Pull Request或Issue。
