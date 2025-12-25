# 🏗️ 架构设计文档

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                     用户界面层                            │
│                   (Chainlit UI)                         │
│                      app.py                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Agent 层                              │
│              (智能决策与协调)                              │
│                                                          │
│  ┌────────────────────────────────────────────┐        │
│  │         TravelAgent                        │        │
│  │  • 接收用户请求                              │        │
│  │  • 理解意图                                 │        │
│  │  • 选择工具                                 │        │
│  │  • 生成响应                                 │        │
│  └────────────────────────────────────────────┘        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Tools 层                               │
│                (功能实现)                                 │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │get_          │  │check_        │  │recommend_    │ │
│  │destinations  │  │availability  │  │destination   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Data 层                                │
│              (数据存储与访问)                              │
│                                                          │
│  • 目的地数据库 (destinations_db)                        │
│  • 对话历史 (ChatHistory)                               │
│  • 用户会话 (User Session)                              │
└─────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. 用户界面层 (UI Layer)

**文件**: `app.py`

**职责**:
- 接收用户输入
- 显示 Agent 响应
- 管理聊天会话
- 提供交互控件

**关键函数**:
```python
@cl.on_chat_start   # 初始化会话
@cl.on_message      # 处理消息
@cl.on_chat_end     # 结束会话
```

### 2. Agent 层 (Agent Layer)

**文件**: `agents/travel_agent.py`

**职责**:
- 理解用户意图
- 选择合适的工具
- 协调工具执行
- 生成最终响应
- 维护对话上下文

**核心流程**:
```
用户输入 → 意图识别 → 工具选择 → 工具执行 → 结果整合 → 响应生成
```

**关键组件**:
- `Kernel`: Semantic Kernel 内核
- `ChatCompletionAgent`: 对话代理
- `ChatHistory`: 对话历史管理
- `FunctionChoiceBehavior`: 工具选择策略

### 3. Tools 层 (Tools Layer)

**文件**: `tools/travel_tools.py`

**职责**:
- 实现具体功能
- 提供工具描述
- 验证输入参数
- 返回结构化结果

**工具定义规范**:
```python
@kernel_function(description="清晰的功能描述")
def tool_name(
    self,
    param: Annotated[type, "参数描述"]
) -> Annotated[type, "返回值描述"]:
    # 实现逻辑
    return result
```

### 4. Data 层 (Data Layer)

**数据结构**:

```python
# 目的地数据模型
{
    "city_name": {
        "available": bool,
        "next_available": str,
        "features": list[str],
        "weather": str
    }
}

# 对话历史
ChatHistory {
    messages: [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
}
```

## 数据流

### 完整请求流程

```
1. 用户输入
   "巴黎现在可以预订吗?"
        │
        ▼
2. Chainlit 接收消息
   app.py: @cl.on_message
        │
        ▼
3. 传递给 Agent
   agent.chat(message)
        │
        ▼
4. Agent 分析意图
   • 识别: 查询操作
   • 目标: 巴黎
   • 需求: 可用性
        │
        ▼
5. 选择工具
   check_destination_availability
        │
        ▼
6. 执行工具
   tools.check_destination_availability("巴黎")
        │
        ▼
7. 返回结果
   {
     "available": true,
     "features": [...],
     "weather": "..."
   }
        │
        ▼
8. Agent 生成响应
   "巴黎现在可以预订! 特色包括..."
        │
        ▼
9. 显示给用户
   Chainlit UI 渲染
```

## 设计模式

### 1. Plugin Pattern (插件模式)

**目的**: 模块化工具管理

```python
# 工具定义
class TravelToolsPlugin:
    @kernel_function(...)
    def tool_1(self): ...
    
    @kernel_function(...)
    def tool_2(self): ...

# 注册插件
kernel.add_plugin(TravelToolsPlugin(), plugin_name="travel")
```

**优势**:
- 易于扩展
- 解耦工具实现
- 支持动态加载

### 2. Agent Pattern (代理模式)

**目的**: 智能决策和任务执行

```python
class TravelAgent:
    def __init__(self):
        self.kernel = Kernel()
        self.agent = ChatCompletionAgent(...)
        self.chat_history = ChatHistory()
    
    async def chat(self, message):
        # 决策 + 执行 + 响应
        pass
```

**优势**:
- 封装复杂逻辑
- 自主决策
- 上下文感知

### 3. Strategy Pattern (策略模式)

**目的**: 灵活的工具选择策略

```python
# Auto: Agent 自动选择
settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

# Required: 必须使用工具
settings.function_choice_behavior = FunctionChoiceBehavior.Required()

# None: 不使用工具
settings.function_choice_behavior = FunctionChoiceBehavior.NoneInvoke()
```

## 扩展点

### 1. 添加新工具

**步骤**:
1. 在 `tools/` 创建新的工具文件
2. 定义工具函数 (使用 `@kernel_function`)
3. 在 Agent 中注册插件

**示例**:
```python
# tools/weather_tools.py
class WeatherToolsPlugin:
    @kernel_function(description="获取天气信息")
    def get_weather(self, city: str) -> str:
        # 实现
        return weather_info

# agents/travel_agent.py
self.kernel.add_plugin(WeatherToolsPlugin(), plugin_name="weather")
```

### 2. 实现多 Agent 协作

**架构**:
```
CoordinatorAgent (协调器)
    ├── FlightAgent (航班)
    ├── HotelAgent (酒店)
    └── ActivityAgent (活动)
```

**实现**:
```python
class CoordinatorAgent:
    def __init__(self):
        self.agents = {
            "flight": FlightAgent(),
            "hotel": HotelAgent(),
            "activity": ActivityAgent()
        }
    
    async def process(self, task):
        # 任务分配
        # 结果汇总
        pass
```

### 3. 添加规划功能

**创建规划器**:
```python
# planners/task_planner.py
class TaskPlanner:
    async def create_plan(self, request):
        # 分解任务
        # 排序优先级
        # 生成计划
        return plan
    
    async def execute_plan(self, plan):
        # 顺序执行
        # 依赖管理
        # 结果收集
        return results
```

### 4. 集成 MCP

**MCP 服务器**:
```python
# mcp/travel_mcp.py
class TravelMCPServer:
    def list_resources(self):
        return [...]
    
    def read_resource(self, uri):
        return data

# 在 Agent 中使用
@kernel_function(description="从 MCP 获取数据")
def fetch_mcp_data(self, uri: str):
    return mcp_server.read_resource(uri)
```

## 性能优化

### 1. 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_data(key):
    return expensive_operation(key)
```

### 2. 并行执行

```python
import asyncio

async def parallel_tasks():
    tasks = [
        agent1.process(task1),
        agent2.process(task2),
        agent3.process(task3)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

### 3. 流式输出

```python
async def stream_response(message):
    async for chunk in agent.invoke_stream(message):
        yield chunk
        # 实时显示
```

## 安全考虑

### 1. 输入验证

```python
def validate_input(user_input: str) -> bool:
    # 长度检查
    if len(user_input) > 1000:
        return False
    
    # 敏感内容过滤
    if contains_sensitive_info(user_input):
        return False
    
    return True
```

### 2. 工具权限控制

```python
class SecureToolsPlugin:
    def __init__(self, user_permissions):
        self.permissions = user_permissions
    
    @kernel_function(...)
    def restricted_tool(self):
        if not self.permissions.can_access("restricted"):
            raise PermissionError()
        # 执行操作
```

### 3. 数据隔离

```python
# 每个用户独立的会话
cl.user_session.set("agent", user_agent)
cl.user_session.set("data", user_data)
```

## 监控和日志

### 日志级别

```python
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

logger.info("用户请求: ...")
logger.warning("工具调用失败: ...")
logger.error("系统错误: ...")
```

### 性能指标

```python
class Metrics:
    def __init__(self):
        self.request_count = 0
        self.avg_response_time = 0
        self.error_count = 0
    
    def record_request(self, duration):
        self.request_count += 1
        self.avg_response_time = (
            (self.avg_response_time * (self.request_count - 1) + duration) 
            / self.request_count
        )
```

## 测试策略

### 单元测试

```python
@pytest.mark.asyncio
async def test_tool():
    tool = TravelToolsPlugin()
    result = tool.get_destinations()
    assert len(result) > 0
```

### 集成测试

```python
@pytest.mark.asyncio
async def test_agent_workflow():
    agent = TravelAgent()
    response = await agent.chat("查询巴黎")
    assert "巴黎" in response
```

### 端到端测试

```python
@pytest.mark.asyncio
async def test_full_conversation():
    # 模拟完整对话流程
    pass
```

## 部署架构

### 本地部署

```
用户 → Chainlit (localhost:8000) → Agent → Tools → Data
```

### 生产部署

```
用户 → Load Balancer
        ↓
    Container 1 (Chainlit + Agent)
    Container 2 (Chainlit + Agent)
    Container 3 (Chainlit + Agent)
        ↓
    Shared Redis (Session)
        ↓
    Database (Data)
```

## 总结

这个架构设计:
- ✅ **模块化**: 清晰的层次划分
- ✅ **可扩展**: 易于添加新功能
- ✅ **可维护**: 代码组织良好
- ✅ **高性能**: 支持并行和缓存
- ✅ **安全**: 输入验证和权限控制

通过这个架构,你可以构建强大、灵活的 AI Agent 应用!
