# 架构文档

## 概述

AI API Toolkit 是一个通用的AI接口预取接入工具，提供了统一的接口来访问多个AI服务提供商，并具有智能缓存和预取功能。

## 架构设计

### 核心组件

```
ai-api-toolkit/
├── base.py              # 基础类和数据结构
├── providers.py         # AI提供商适配器
├── cache.py             # 缓存管理
├── client.py            # 主客户端
├── config.py            # 配置管理
├── __init__.py          # 包入口
├── requirements.txt     # 依赖管理
├── examples.py          # 使用示例
├── example_notebook.ipynb # Jupyter示例
├── test_basic.py        # 基础测试
├── .env.example         # 环境变量模板
├── README.md            # 快速开始
├── USAGE.md             # 详细使用指南
└── ARCHITECTURE.md      # 架构文档（本文件）
```

### 组件说明

#### 1. base.py - 基础抽象层

**核心类**:

- `Message`: 消息数据类
  - `role`: 角色（system, user, assistant）
  - `content`: 消息内容
  - `name`: 可选名称

- `CompletionResponse`: 响应数据类
  - `content`: 生成的内容
  - `model`: 使用的模型
  - `usage`: Token使用情况
  - `finish_reason`: 完成原因
  - `provider`: 提供商名称
  - `cached`: 是否来自缓存
  - `latency_ms`: 延迟时间

- `BaseAIProvider`: 提供商抽象基类
  - `initialize()`: 初始化客户端
  - `complete()`: 生成完成响应
  - `stream_complete()`: 流式生成
  - `get_provider_name()`: 获取提供商名称

**设计模式**: 策略模式（Strategy Pattern）

#### 2. providers.py - 提供商适配器

**实现的提供商**:

- `OpenAIProvider`: OpenAI适配器
- `AzureOpenAIProvider`: Azure OpenAI适配器
- `AnthropicProvider`: Anthropic/Claude适配器
- `GoogleProvider`: Google Gemini适配器

**扩展性**: 通过继承`BaseAIProvider`可轻松添加新提供商

**设计模式**: 适配器模式（Adapter Pattern）

#### 3. cache.py - 缓存层

**CacheManager**:

- 支持内存缓存（LRU淘汰）
- 支持Redis缓存
- 可配置TTL和容量
- 自动生成缓存键（基于请求参数）

**PrefetchManager**:

- 批量预取请求
- 预取队列管理
- 异步并发预取

**缓存键生成**: SHA256哈希（基于消息、模型、温度等参数）

**设计模式**: 代理模式（Proxy Pattern）

#### 4. client.py - 统一客户端

**AIClient**:

核心功能：
- 统一的API接口
- 自动缓存管理
- 预取支持
- 统计信息收集
- 辅助方法（创建消息等）

请求流程：
```
User Request
    ↓
AIClient.complete()
    ↓
检查缓存
    ├─ 命中 → 返回缓存结果
    └─ 未命中
        ↓
    Provider.complete()
        ↓
    写入缓存
        ↓
    返回结果
```

**设计模式**: 外观模式（Facade Pattern）

#### 5. config.py - 配置管理

**配置类**:

- `ProviderConfig`: 提供商配置
- `CacheConfig`: 缓存配置
- `ClientConfig`: 客户端配置

**配置来源**:
1. 环境变量（推荐）
2. 代码配置
3. 配置文件（通过环境变量）

## 数据流

### 1. 完成请求流程

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│ AIClient    │◄────►│ CacheManager │
└──────┬──────┘      └──────────────┘
       │
       ▼
┌─────────────┐
│  Provider   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  AI API     │
└─────────────┘
```

### 2. 预取流程

```
┌──────────────────┐
│ Messages List    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ PrefetchManager  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Concurrent Fetch │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ CacheManager     │
└──────────────────┘
```

### 3. 缓存机制

```
Request → Hash(params) → Cache Key
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
         ┌────────────┐            ┌──────────────┐
         │ Memory LRU │            │    Redis     │
         └────────────┘            └──────────────┘
```

## 关键设计决策

### 1. 为什么使用异步API？

- AI API调用通常耗时较长（几秒）
- 异步可以更好地利用等待时间
- 支持高并发场景
- 更好的资源利用率

### 2. 为什么使用双层缓存？

- 内存缓存：低延迟，适合单实例
- Redis缓存：持久化，适合多实例
- 可根据场景灵活选择

### 3. 缓存键如何生成？

基于所有影响输出的参数：
- 消息内容
- 模型名称
- 温度参数
- 其他配置

使用SHA256确保：
- 唯一性
- 固定长度
- 不可逆（隐私保护）

### 4. 为什么不缓存流式响应？

- 流式响应的价值在于即时反馈
- 缓存会失去流式体验
- 实现复杂度高
- 收益有限

### 5. 提供商隔离

每个提供商独立实现，互不影响：
- 易于维护
- 易于扩展
- 失败隔离

## 性能优化

### 1. 缓存策略

- LRU淘汰：保留最常用的缓存
- TTL过期：避免陈旧数据
- 大小限制：防止内存溢出

### 2. 预取优化

- 并发请求：同时发送多个请求
- 异步处理：不阻塞主流程
- 智能预测：基于使用模式

### 3. 连接复用

- 提供商客户端复用
- Redis连接池
- HTTP连接池（底层库处理）

## 安全考虑

### 1. API密钥管理

- 推荐使用环境变量
- 不在代码中硬编码
- 不记录到日志

### 2. 缓存安全

- 缓存键不包含敏感信息
- Redis使用密码认证
- 支持加密连接

### 3. 错误处理

- 不泄露敏感信息
- 优雅降级
- 异常捕获

## 扩展性

### 1. 添加新提供商

```python
from base import BaseAIProvider, Message, CompletionResponse

class NewProvider(BaseAIProvider):
    def initialize(self):
        # 初始化代码
        pass
    
    async def complete(self, messages, model, **kwargs):
        # 实现完成逻辑
        pass
    
    async def stream_complete(self, messages, model, **kwargs):
        # 实现流式逻辑
        pass
    
    def get_provider_name(self):
        return "new_provider"
```

在`client.py`中注册：

```python
PROVIDER_MAP = {
    ...
    "new_provider": NewProvider
}
```

### 2. 自定义缓存策略

继承`CacheManager`并重写方法：

```python
class CustomCacheManager(CacheManager):
    def get(self, cache_key):
        # 自定义获取逻辑
        pass
    
    def set(self, cache_key, data):
        # 自定义设置逻辑
        pass
```

### 3. 添加中间件

在`AIClient.complete()`中添加钩子：

```python
class AIClient:
    def __init__(self, ...):
        self.middlewares = []
    
    async def complete(self, messages, ...):
        # 前置中间件
        for mw in self.middlewares:
            messages = await mw.before(messages)
        
        # 原有逻辑
        response = await self.provider.complete(...)
        
        # 后置中间件
        for mw in reversed(self.middlewares):
            response = await mw.after(response)
        
        return response
```

## 测试策略

### 1. 单元测试

- 测试各个组件独立功能
- Mock外部依赖
- 覆盖边界条件

### 2. 集成测试

- 测试组件间交互
- 使用真实API（受限）
- 测试缓存和预取

### 3. 性能测试

- 缓存命中率
- 响应延迟
- 并发性能

## 未来改进

### 1. 功能增强

- [ ] 批量请求支持
- [ ] 更多提供商（Cohere, AI21等）
- [ ] 函数调用支持
- [ ] 嵌入向量支持

### 2. 性能优化

- [ ] 智能预取（基于历史）
- [ ] 缓存预热
- [ ] 请求合并

### 3. 可观测性

- [ ] 日志集成
- [ ] 指标导出（Prometheus）
- [ ] 追踪支持（OpenTelemetry）

### 4. 开发体验

- [ ] 类型提示完善
- [ ] 更多示例
- [ ] CLI工具

## 总结

AI API Toolkit 通过合理的架构设计，实现了：

1. **统一性**: 一套API访问多个提供商
2. **性能**: 智能缓存和预取
3. **可扩展**: 易于添加新功能和提供商
4. **易用性**: 简洁的API和丰富的文档

适用于：
- AI应用开发
- 多模型对比
- 成本优化
- 性能优化
