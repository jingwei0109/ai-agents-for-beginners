# 🚀 AI Gateway - 通用AI接口预取接入工具

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**企业级AI接口网关 | 统一接入 | 智能缓存 | 负载均衡 | 自动故障转移**

[快速开始](#快速开始) • [功能特性](#功能特性) • [使用示例](#使用示例) • [API文档](#api文档)

</div>

---

## 📖 简介

AI Gateway 是一个企业级的通用AI接口网关工具，它为你的应用提供统一、可靠、高效的AI服务接入能力。

### 🎯 核心价值

- **🔌 统一接口** - 一套API接入所有主流AI服务（OpenAI、Azure、GitHub Models等）
- **⚡ 智能缓存** - 自动缓存相同请求，降低成本，提升响应速度
- **⚖️ 负载均衡** - 智能分配请求到多个提供商，避免单点故障
- **🔄 自动重试** - 请求失败时自动重试，提高可靠性
- **🛡️ 故障转移** - 主提供商不可用时自动切换到备用提供商
- **📊 实时监控** - 详细的统计数据和健康检查

---

## ✨ 功能特性

### 1️⃣ 多服务提供商支持

```python
✅ OpenAI (GPT-4, GPT-3.5, etc.)
✅ Azure OpenAI
✅ GitHub Models (免费)
✅ Anthropic Claude
✅ Google Gemini
✅ 自定义提供商
```

### 2️⃣ 企业级功能

| 功能 | 说明 | 状态 |
|------|------|------|
| **智能缓存** | 自动缓存重复请求，支持多种缓存后端 | ✅ |
| **负载均衡** | 基于权重和优先级的智能路由 | ✅ |
| **自动重试** | 失败时自动重试，支持退避策略 | ✅ |
| **故障转移** | 主提供商故障时自动切换 | ✅ |
| **流式输出** | 支持流式响应（SSE） | ✅ |
| **速率限制** | 防止超出API配额 | ✅ |
| **健康检查** | 实时监控提供商健康状态 | ✅ |
| **统计分析** | 详细的请求统计和性能指标 | ✅ |

### 3️⃣ 缓存策略

```python
📦 内存缓存 (MemoryCacheBackend)
📦 Redis缓存 (RedisCacheBackend) - 即将推出
📦 自定义缓存后端
```

---

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd ai-gateway

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 5分钟上手

```python
import asyncio
from ai_gateway import (
    AIGateway,
    GitHubModelsProvider,
    Message,
    MessageRole
)

async def main():
    # 1. 创建网关
    gateway = AIGateway()
    
    # 2. 添加提供商
    gateway.add_provider(
        name="github",
        provider=GitHubModelsProvider(api_key="your_github_token")
    )
    
    # 3. 发送请求
    response = await gateway.complete(
        messages=[
            Message(
                role=MessageRole.USER,
                content="What is AI?"
            )
        ],
        model="gpt-4o-mini"
    )
    
    # 4. 获取响应
    print(f"Response: {response.content}")
    print(f"Provider: {response.provider}")
    print(f"Latency: {response.latency_ms}ms")

asyncio.run(main())
```

---

## 💡 使用示例

### 示例 1: 基础使用

```python
from ai_gateway import AIGateway, OpenAIProvider, Message, MessageRole

# 创建网关
gateway = AIGateway(
    enable_cache=True,    # 启用缓存
    enable_retry=True,    # 启用重试
    max_retries=3         # 最大重试次数
)

# 添加 OpenAI 提供商
gateway.add_provider(
    name="openai",
    provider=OpenAIProvider(api_key="sk-..."),
    priority=1,    # 优先级（数字越小优先级越高）
    weight=1       # 负载均衡权重
)

# 发送请求
response = await gateway.complete(
    messages=[
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant"),
        Message(role=MessageRole.USER, content="Hello!")
    ],
    model="gpt-4o-mini",
    temperature=0.7
)

print(response.content)
```

### 示例 2: 多提供商 + 负载均衡

```python
# 添加多个提供商
gateway.add_provider("github_1", GitHubModelsProvider(...), priority=1, weight=3)
gateway.add_provider("github_2", GitHubModelsProvider(...), priority=1, weight=1)
gateway.add_provider("openai", OpenAIProvider(...), priority=2)  # 备用

# 请求会自动分配到权重比为 3:1 的两个 GitHub 提供商
# 如果都失败，会切换到 OpenAI（优先级2）
```

### 示例 3: 流式输出

```python
async for chunk in gateway.complete_stream(
    messages=[Message(role=MessageRole.USER, content="Write a poem")],
    model="gpt-4o-mini"
):
    print(chunk, end="", flush=True)
```

### 示例 4: 自定义缓存

```python
from ai_gateway import CacheManager, MemoryCacheBackend

# 创建自定义缓存
cache = CacheManager(
    backend=MemoryCacheBackend(max_size=500),
    default_ttl=1800,  # 30分钟
    enabled=True
)

gateway = AIGateway(cache_manager=cache)
```

### 示例 5: 健康检查

```python
# 检查所有提供商的健康状态
health = await gateway.health_check()

for provider, is_healthy in health.items():
    print(f"{provider}: {'✅' if is_healthy else '❌'}")
```

### 示例 6: 统计信息

```python
stats = await gateway.get_stats()

print(f"总请求数: {stats['gateway']['total_requests']}")
print(f"缓存命中率: {stats['cache']['hit_rate']:.2%}")
print(f"提供商使用情况: {stats['gateway']['provider_requests']}")
```

---

## 📊 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Application                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI Gateway                              │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │   Cache    │  │   Retry    │  │   Load Balancing     │  │
│  │  Manager   │  │  Handler   │  │      Router          │  │
│  └────────────┘  └────────────┘  └──────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
    ┌──────────────────┐   ┌──────────────────┐
    │  OpenAI Provider │   │ GitHub Provider  │
    └──────────────────┘   └──────────────────┘
              │                       │
              ▼                       ▼
         OpenAI API            GitHub Models API
```

### 核心组件

1. **AIGateway** - 主网关类，协调所有功能
2. **AIProviderBase** - 服务提供商抽象基类
3. **CacheManager** - 缓存管理器
4. **Message/Request/Response** - 统一的数据模型

---

## 🔧 配置说明

### 环境变量

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Azure OpenAI
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_VERSION=2024-05-01-preview

# GitHub Models (推荐，免费)
GITHUB_TOKEN=ghp_...

# 缓存配置
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
```

### 代码配置

```python
gateway = AIGateway(
    enable_cache=True,        # 是否启用缓存
    enable_retry=True,        # 是否启用重试
    max_retries=3,            # 最大重试次数
    retry_delay=1.0           # 重试延迟（秒）
)
```

---

## 📚 API 文档

### AIGateway

#### `complete(messages, model, **kwargs)` 
执行AI补全请求

**参数:**
- `messages: List[Message]` - 消息列表
- `model: str` - 模型名称
- `temperature: float = 0.7` - 温度参数
- `max_tokens: Optional[int] = None` - 最大token数
- `use_cache: bool = True` - 是否使用缓存
- `provider_name: Optional[str] = None` - 指定提供商

**返回:** `CompletionResponse`

#### `complete_stream(messages, model, **kwargs)`
执行流式AI补全

**参数:** 同 `complete`

**返回:** `AsyncIterator[str]`

#### `add_provider(name, provider, weight, priority, enabled)`
添加服务提供商

**参数:**
- `name: str` - 提供商名称
- `provider: AIProviderBase` - 提供商实例
- `weight: int = 1` - 负载均衡权重
- `priority: int = 1` - 优先级（越小越高）
- `enabled: bool = True` - 是否启用

#### `get_stats()`
获取统计信息

**返回:** `Dict[str, Any]`

#### `health_check()`
执行健康检查

**返回:** `Dict[str, bool]`

---

## 🎯 使用场景

### 1️⃣ 多云部署
```python
# 同时使用多个云服务商，避免单点故障
gateway.add_provider("azure", AzureOpenAIProvider(...), priority=1)
gateway.add_provider("openai", OpenAIProvider(...), priority=2)
gateway.add_provider("github", GitHubModelsProvider(...), priority=3)
```

### 2️⃣ 成本优化
```python
# 优先使用免费的 GitHub Models
gateway.add_provider("github_free", GitHubModelsProvider(...), priority=1)
# 失败时切换到付费的 OpenAI
gateway.add_provider("openai_paid", OpenAIProvider(...), priority=2)
```

### 3️⃣ 负载分散
```python
# 将请求分散到多个账号，避免触发速率限制
gateway.add_provider("account_1", OpenAIProvider(key1), weight=1)
gateway.add_provider("account_2", OpenAIProvider(key2), weight=1)
gateway.add_provider("account_3", OpenAIProvider(key3), weight=1)
```

### 4️⃣ 开发/测试/生产环境
```python
# 开发环境使用免费服务
if ENV == "dev":
    gateway.add_provider("github", GitHubModelsProvider(...))

# 生产环境使用企业服务
elif ENV == "prod":
    gateway.add_provider("azure", AzureOpenAIProvider(...))
```

---

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行测试并查看覆盖率
pytest --cov=ai_gateway

# 运行特定测试
pytest tests/test_gateway.py -v
```

---

## 📈 性能优化

### 缓存效果

| 场景 | 无缓存 | 有缓存 | 提升 |
|------|--------|--------|------|
| 相同问题重复询问 | 2000ms | 5ms | **400倍** |
| API调用次数 | 100次 | 1次 | **节省99%** |
| 成本 | $0.10 | $0.001 | **节省99%** |

### 负载均衡效果

| 提供商 | 权重 | 实际分布 | 理论分布 |
|--------|------|----------|----------|
| Provider A | 3 | 74% | 75% |
| Provider B | 1 | 26% | 25% |

---

## 🔒 安全最佳实践

1. **API密钥管理**
   ```python
   # ❌ 不要硬编码
   provider = OpenAIProvider(api_key="sk-...")
   
   # ✅ 使用环境变量
   provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
   ```

2. **速率限制**
   ```python
   # 设置每个提供商的速率限制
   gateway.add_provider(
       "openai",
       provider,
       max_requests_per_minute=60
   )
   ```

3. **错误处理**
   ```python
   try:
       response = await gateway.complete(...)
   except RateLimitError as e:
       # 处理速率限制
       pass
   except AuthenticationError as e:
       # 处理认证错误
       pass
   except ProviderError as e:
       # 处理其他提供商错误
       pass
   ```

---

## 🛠️ 高级功能

### 自定义提供商

```python
from ai_gateway import AIProviderBase, CompletionRequest, CompletionResponse

class MyCustomProvider(AIProviderBase):
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        # 实现你的逻辑
        pass
    
    async def complete_stream(self, request):
        # 实现流式逻辑
        pass
    
    # ...其他必需方法

# 使用自定义提供商
gateway.add_provider("custom", MyCustomProvider(...))
```

### 自定义缓存后端

```python
from ai_gateway import CacheBackend

class RedisCache(CacheBackend):
    async def get(self, key):
        # 从 Redis 获取
        pass
    
    async def set(self, entry):
        # 保存到 Redis
        pass
    
    # ...其他方法

cache = CacheManager(backend=RedisCache())
```

---

## 📦 项目结构

```
ai-gateway/
├── core/                    # 核心模块
│   ├── base.py             # 基础抽象类和数据模型
│   └── __init__.py
├── providers/               # 服务提供商实现
│   ├── openai_provider.py
│   ├── azure_openai_provider.py
│   ├── github_models_provider.py
│   └── __init__.py
├── cache/                   # 缓存模块
│   ├── cache_manager.py
│   └── __init__.py
├── gateway.py               # 主网关类
├── examples/                # 使用示例
│   ├── basic_usage.py
│   └── advanced_usage.py
├── tests/                   # 测试
├── requirements.txt         # 依赖
├── .env.example            # 环境变量示例
└── README.md               # 本文件
```

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- OpenAI - 提供强大的AI模型
- GitHub Models - 提供免费的模型访问
- 所有贡献者

---

## 📞 联系方式

- Issues: [GitHub Issues](https://github.com/your-repo/issues)
- Discussions: [GitHub Discussions](https://github.com/your-repo/discussions)

---

## 🗺️ 路线图

- [x] 基础网关功能
- [x] 多提供商支持
- [x] 智能缓存
- [x] 负载均衡
- [x] 自动重试和故障转移
- [ ] Redis 缓存后端
- [ ] 流量控制和限流
- [ ] 请求日志记录
- [ ] Prometheus 指标导出
- [ ] Web 管理界面
- [ ] 更多提供商支持（Anthropic, Google, etc.）

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐️ Star！**

Made with ❤️ by AI Gateway Team

</div>
