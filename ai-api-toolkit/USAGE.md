# 详细使用指南

## 目录

1. [快速开始](#快速开始)
2. [核心概念](#核心概念)
3. [提供商配置](#提供商配置)
4. [缓存策略](#缓存策略)
5. [预取机制](#预取机制)
6. [高级用法](#高级用法)
7. [性能优化](#性能优化)
8. [常见问题](#常见问题)

## 快速开始

### 安装依赖

```bash
# 基础安装
pip install openai

# 完整安装（所有提供商）
pip install openai anthropic google-generativeai redis
```

### 最简示例

```python
import asyncio
from ai_api_toolkit import AIClient, Message

async def main():
    client = AIClient(
        provider="openai",
        api_key="your-api-key"
    )
    
    messages = [Message(role="user", content="Hello!")]
    response = await client.complete(messages, model="gpt-4o-mini")
    print(response.content)

asyncio.run(main())
```

## 核心概念

### Message（消息）

消息是与AI交互的基本单元。

```python
from ai_api_toolkit import Message

# 创建消息
msg = Message(role="user", content="Hello")

# 支持的角色
# - system: 系统提示词
# - user: 用户消息
# - assistant: AI助手响应
```

### CompletionResponse（响应）

完成响应包含AI生成的内容和元数据。

```python
response = await client.complete(messages, model="gpt-4o-mini")

print(response.content)        # 生成的文本
print(response.model)          # 使用的模型
print(response.usage)          # Token使用情况
print(response.finish_reason)  # 完成原因
print(response.provider)       # 提供商名称
print(response.cached)         # 是否来自缓存
print(response.latency_ms)     # 延迟（毫秒）
```

## 提供商配置

### OpenAI

```python
client = AIClient(
    provider="openai",
    api_key="sk-...",
    base_url="https://api.openai.com/v1"  # 可选
)

response = await client.complete(
    messages=messages,
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000
)
```

支持的模型：
- gpt-4o
- gpt-4o-mini
- gpt-4-turbo
- gpt-3.5-turbo

### Azure OpenAI

```python
client = AIClient(
    provider="azure_openai",
    api_key="your-azure-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_version="2024-02-15-preview"
)

response = await client.complete(
    messages=messages,
    model="your-deployment-name"
)
```

### Anthropic (Claude)

```python
client = AIClient(
    provider="anthropic",
    api_key="sk-ant-..."
)

response = await client.complete(
    messages=messages,
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024  # Anthropic需要max_tokens
)
```

支持的模型：
- claude-3-5-sonnet-20241022
- claude-3-opus-20240229
- claude-3-sonnet-20240229
- claude-3-haiku-20240307

### Google (Gemini)

```python
client = AIClient(
    provider="google",
    api_key="your-google-key"
)

response = await client.complete(
    messages=messages,
    model="gemini-pro"
)
```

## 缓存策略

### 内存缓存

默认启用，使用LRU淘汰策略。

```python
client = AIClient(
    provider="openai",
    api_key="your-key",
    enable_cache=True,
    cache_ttl=3600,        # 1小时过期
    cache_max_size=1000    # 最多1000条
)
```

### Redis缓存

适用于生产环境和多实例部署。

```python
client = AIClient(
    provider="openai",
    api_key="your-key",
    enable_cache=True,
    use_redis=True,
    redis_url="redis://localhost:6379/0"
)
```

### 缓存键生成

缓存键基于以下参数：
- 消息内容
- 模型名称
- 温度参数
- 其他参数

相同的参数将生成相同的缓存键。

### 缓存管理

```python
# 清空缓存
client.clear_cache()

# 禁用单次请求的缓存
response = await client.complete(
    messages=messages,
    model="gpt-4o-mini",
    use_cache=False
)

# 查看缓存统计
stats = client.get_stats()
print(stats['cache_hit_rate'])
```

## 预取机制

### 批量预取

适用于可预测的请求。

```python
# 准备多个请求
messages_list = [
    [Message(role="user", content="Question 1")],
    [Message(role="user", content="Question 2")],
    [Message(role="user", content="Question 3")]
]

# 批量预取
await client.prefetch(
    messages_list=messages_list,
    model="gpt-4o-mini"
)

# 后续请求将从缓存获取
for messages in messages_list:
    response = await client.complete(messages, model="gpt-4o-mini")
    # response.cached == True
```

### 预取队列

适用于异步场景。

```python
# 添加到队列
client.add_to_prefetch_queue(messages1, model="gpt-4o-mini")
client.add_to_prefetch_queue(messages2, model="gpt-4o-mini")

# 稍后处理
await client.process_prefetch_queue()
```

## 高级用法

### 流式响应

```python
async for chunk in client.stream_complete(
    messages=messages,
    model="gpt-4o-mini"
):
    print(chunk, end="", flush=True)
```

### 多轮对话

```python
conversation = [
    Message(role="system", content="You are a helpful assistant")
]

# 第一轮
conversation.append(Message(role="user", content="Hi"))
response = await client.complete(conversation, model="gpt-4o-mini")
conversation.append(Message(role="assistant", content=response.content))

# 第二轮
conversation.append(Message(role="user", content="Tell me more"))
response = await client.complete(conversation, model="gpt-4o-mini")
```

### 并发请求

```python
import asyncio

async def process_request(messages):
    return await client.complete(messages, model="gpt-4o-mini")

# 并发处理多个请求
tasks = [process_request(msgs) for msgs in messages_list]
responses = await asyncio.gather(*tasks)
```

### 错误处理

```python
try:
    response = await client.complete(messages, model="gpt-4o-mini")
except Exception as e:
    print(f"错误: {e}")
    # 处理错误
```

### 使用配置文件

```python
from ai_api_toolkit.config import ClientConfig

# 从环境变量
config = ClientConfig.from_env("openai")
client = AIClient(**config.to_client_kwargs())

# 或手动配置
from ai_api_toolkit.config import ProviderConfig, CacheConfig

provider_config = ProviderConfig(
    provider="openai",
    api_key="your-key"
)

cache_config = CacheConfig(
    enabled=True,
    ttl_seconds=7200
)

config = ClientConfig(
    provider_config=provider_config,
    cache_config=cache_config
)

client = AIClient(**config.to_client_kwargs())
```

## 性能优化

### 1. 启用缓存

对于重复的请求，缓存可以节省90%以上的时间和成本。

```python
# 好的实践
client = AIClient(
    provider="openai",
    api_key="your-key",
    enable_cache=True
)
```

### 2. 使用预取

如果能预测用户需求，使用预取可以实现"即时"响应。

```python
# 在用户选择之前预取所有可能的响应
await client.prefetch(possible_messages, model="gpt-4o-mini")
```

### 3. 选择合适的模型

- 简单任务: gpt-4o-mini, claude-3-haiku
- 复杂任务: gpt-4o, claude-3-5-sonnet
- 平衡选择: gpt-4o-mini（性价比高）

### 4. 调整温度参数

- temperature=0: 确定性输出，适合缓存
- temperature>0: 随机性输出，不适合缓存

### 5. Redis缓存

生产环境使用Redis可以：
- 跨实例共享缓存
- 持久化缓存
- 更大的缓存容量

### 6. 监控统计

定期检查统计信息，优化缓存策略。

```python
stats = client.get_stats()
print(f"缓存命中率: {stats['cache_hit_rate']:.2%}")

if stats['cache_hit_rate'] < 0.3:
    # 缓存命中率太低，考虑调整策略
    pass
```

## 常见问题

### Q: 如何处理API密钥？

A: 推荐使用环境变量：

```bash
export OPENAI_API_KEY=your-key
```

```python
import os
client = AIClient(
    provider="openai",
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### Q: 缓存会过期吗？

A: 是的，缓存有TTL（生存时间）。默认1小时，可以配置：

```python
client = AIClient(
    provider="openai",
    api_key="your-key",
    cache_ttl=7200  # 2小时
)
```

### Q: 如何禁用缓存？

A: 有两种方式：

```python
# 方式1：创建客户端时禁用
client = AIClient(
    provider="openai",
    api_key="your-key",
    enable_cache=False
)

# 方式2：单次请求禁用
response = await client.complete(
    messages=messages,
    model="gpt-4o-mini",
    use_cache=False
)
```

### Q: 流式响应支持缓存吗？

A: 不支持。流式响应始终从API获取。

### Q: 如何切换提供商？

A: 只需更改provider参数：

```python
# OpenAI
client1 = AIClient(provider="openai", api_key="key1")

# Anthropic
client2 = AIClient(provider="anthropic", api_key="key2")

# 使用相同的接口
response = await client1.complete(messages, model="gpt-4o-mini")
response = await client2.complete(messages, model="claude-3-5-sonnet-20241022")
```

### Q: 支持自定义提供商吗？

A: 支持！继承BaseAIProvider：

```python
from ai_api_toolkit.base import BaseAIProvider

class CustomProvider(BaseAIProvider):
    def initialize(self):
        # 初始化客户端
        pass
    
    async def complete(self, messages, model, **kwargs):
        # 实现完成逻辑
        pass
    
    async def stream_complete(self, messages, model, **kwargs):
        # 实现流式逻辑
        pass
    
    def get_provider_name(self):
        return "custom"
```

### Q: 如何估算token使用？

A: 每次请求的响应都包含token使用信息：

```python
response = await client.complete(messages, model="gpt-4o-mini")
print(response.usage)
# {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30}

# 查看总使用量
stats = client.get_stats()
print(f"总token: {stats['total_tokens']}")
```

### Q: 并发限制？

A: 工具本身没有限制，但要注意：
- API提供商的速率限制
- Redis连接数限制
- 系统资源限制

建议使用semaphore控制并发：

```python
import asyncio

semaphore = asyncio.Semaphore(10)  # 最多10个并发

async def limited_complete(messages):
    async with semaphore:
        return await client.complete(messages, model="gpt-4o-mini")

tasks = [limited_complete(msgs) for msgs in messages_list]
responses = await asyncio.gather(*tasks)
```

## 更多示例

查看以下文件获取更多示例：
- `examples.py`: Python脚本示例
- `example_notebook.ipynb`: Jupyter Notebook示例
- `README.md`: 快速参考
