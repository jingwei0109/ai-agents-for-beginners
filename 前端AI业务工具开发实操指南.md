# 前端AI业务工具开发实操指南

## 📚 目录
1. [前期准备](#前期准备)
2. [核心概念理解](#核心概念理解)
3. [第一个AI工具：旅游助手](#第一个ai工具旅游助手)
4. [五大核心模块详解](#五大核心模块详解)
5. [完整项目实现](#完整项目实现)
6. [测试与优化](#测试与优化)

---

## 🚀 前期准备

### 1. 环境配置

```bash
# 1. 安装必要的依赖
pip install semantic-kernel
pip install azure-ai-projects
pip install openai
pip install python-dotenv
pip install chainlit  # 用于前端界面

# 2. 配置环境变量
# 创建 .env 文件
```

**.env 文件配置:**
```bash
# 使用 GitHub Models (免费,适合入门)
GITHUB_TOKEN="your_github_personal_access_token"

# 或使用 Azure OpenAI
AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com/"
AZURE_OPENAI_API_KEY="your_api_key"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini"
AZURE_OPENAI_API_VERSION="2024-05-01-preview"
```

### 2. Cursor 项目设置

1. 在 Cursor 中打开项目文件夹
2. 创建以下目录结构:
```
my-ai-tool/
├── .env                    # 环境变量
├── app.py                  # 主应用文件
├── agents/                 # Agent 定义
│   ├── __init__.py
│   ├── base_agent.py
│   └── specialized_agents.py
├── tools/                  # 工具函数
│   ├── __init__.py
│   └── custom_tools.py
├── planners/              # 规划器
│   ├── __init__.py
│   └── task_planner.py
└── requirements.txt       # 依赖列表
```

---

## 🧠 核心概念理解

### Agent (代理)
**定义**: AI Agent 是一个能够感知环境、做出决策并执行动作的智能系统。

**核心要素**:
- 🎯 **目标**: 明确要完成什么任务
- 🛠️ **工具**: 可以调用的函数/API
- 💭 **推理**: 决定下一步做什么
- 📝 **记忆**: 保存对话历史和上下文

### Plan (规划)
**定义**: 将复杂任务分解为多个可执行的子任务。

**关键点**:
- 任务分解
- 优先级排序
- 动态调整

### Ask (询问)
**定义**: 与 LLM 交互,获取响应。

**实现方式**:
- 单次询问
- 流式响应
- 上下文管理

### Tools (工具)
**定义**: Agent 可以调用的函数,用于执行特定操作。

**类型**:
- 数据检索工具
- API 调用工具
- 代码执行工具

### MCP (Model Context Protocol)
**定义**: 标准化的协议,用于 AI 模型与外部工具/数据源的连接。

**优势**:
- 统一接口
- 易于扩展
- 安全可控

---

## 🎯 第一个AI工具：旅游助手

### 目标
创建一个智能旅游助手,能够:
1. 推荐旅游目的地
2. 查询目的地可用性
3. 根据用户偏好制定旅行计划

### 步骤 1: 定义 Tools (工具)

创建 `tools/travel_tools.py`:

```python
from typing import Annotated
from semantic_kernel.functions import kernel_function

class TravelToolsPlugin:
    """旅游工具插件"""
    
    @kernel_function(description="获取可用的旅游目的地列表")
    def get_destinations(self) -> Annotated[str, "返回目的地列表"]:
        """获取旅游目的地"""
        destinations = {
            "Barcelona": {"country": "Spain", "available": False, "price": "$$$"},
            "Paris": {"country": "France", "available": True, "price": "$$$$"},
            "Tokyo": {"country": "Japan", "available": False, "price": "$$$"},
            "Bali": {"country": "Indonesia", "available": True, "price": "$$"},
            "New York": {"country": "USA", "available": True, "price": "$$$$$"}
        }
        
        result = "可用目的地:\n"
        for city, info in destinations.items():
            status = "✅ 可预订" if info["available"] else "❌ 已满"
            result += f"- {city}, {info['country']} - {info['price']} - {status}\n"
        return result
    
    @kernel_function(description="检查特定目的地的详细信息和可用性")
    def check_destination_availability(
        self, 
        destination: Annotated[str, "要查询的目的地名称"]
    ) -> Annotated[str, "返回目的地的详细信息"]:
        """检查目的地可用性"""
        destinations_db = {
            "barcelona": {
                "available": False,
                "next_available": "2025-12-15",
                "features": ["海滩", "建筑", "美食"],
                "weather": "温暖宜人"
            },
            "paris": {
                "available": True,
                "next_available": "即刻",
                "features": ["艺术", "历史", "浪漫"],
                "weather": "温和"
            },
            "tokyo": {
                "available": False,
                "next_available": "2025-12-01",
                "features": ["科技", "文化", "美食"],
                "weather": "四季分明"
            },
            "bali": {
                "available": True,
                "next_available": "即刻",
                "features": ["海滩", "文化", "瑜伽"],
                "weather": "热带气候"
            },
            "new york": {
                "available": True,
                "next_available": "即刻",
                "features": ["都市", "艺术", "购物"],
                "weather": "四季分明"
            }
        }
        
        dest_lower = destination.lower()
        if dest_lower in destinations_db:
            info = destinations_db[dest_lower]
            status = "✅ 现在可预订" if info["available"] else f"❌ 已满,下次可预订: {info['next_available']}"
            return f"""
{destination} 详细信息:
- 状态: {status}
- 特色: {', '.join(info['features'])}
- 天气: {info['weather']}
"""
        return f"抱歉,未找到 {destination} 的信息。"
    
    @kernel_function(description="根据用户预算和偏好推荐目的地")
    def recommend_destination(
        self,
        budget: Annotated[str, "预算等级: low, medium, high"],
        preferences: Annotated[str, "偏好类型,如: 海滩, 文化, 美食"]
    ) -> Annotated[str, "返回推荐的目的地"]:
        """智能推荐目的地"""
        recommendations = {
            "low": {
                "beach": "Bali - 性价比高的海滩度假胜地",
                "culture": "Prague - 历史悠久且经济实惠",
                "food": "Bangkok - 街头美食天堂"
            },
            "medium": {
                "beach": "Barcelona - 海滩与城市完美结合",
                "culture": "Kyoto - 传统日本文化体验",
                "food": "Barcelona - 地中海美食"
            },
            "high": {
                "beach": "Maldives - 奢华海岛度假",
                "culture": "Paris - 世界艺术之都",
                "food": "Tokyo - 米其林餐厅最多的城市"
            }
        }
        
        pref_lower = preferences.lower()
        pref_key = "beach" if "海滩" in pref_lower or "beach" in pref_lower else \
                   "culture" if "文化" in pref_lower or "culture" in pref_lower else \
                   "food"
        
        if budget.lower() in recommendations:
            return f"💡 根据您的预算({budget})和偏好({preferences}),推荐:\n{recommendations[budget.lower()][pref_key]}"
        return "请提供有效的预算等级: low, medium, high"
```

### 步骤 2: 创建 Agent (代理)

创建 `agents/travel_agent.py`:

```python
import os
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.functions import KernelArguments
from openai import AsyncOpenAI

# 导入自定义工具
import sys
sys.path.append('..')
from tools.travel_tools import TravelToolsPlugin

class TravelAgent:
    """旅游助手 Agent"""
    
    def __init__(self):
        load_dotenv()
        
        # 初始化客户端
        self.client = AsyncOpenAI(
            api_key=os.getenv("GITHUB_TOKEN"),
            base_url="https://models.inference.ai.azure.com/"
        )
        
        # 创建 Kernel
        self.kernel = Kernel()
        
        # 添加工具插件
        self.kernel.add_plugin(TravelToolsPlugin(), plugin_name="travel_tools")
        
        # 配置 AI 服务
        service_id = "travel_agent"
        chat_service = OpenAIChatCompletion(
            ai_model_id="gpt-4o-mini",
            async_client=self.client,
            service_id=service_id
        )
        self.kernel.add_service(chat_service)
        
        # 设置函数调用行为
        settings = self.kernel.get_prompt_execution_settings_from_service_id(
            service_id=service_id
        )
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        
        # 创建 Agent
        self.agent = ChatCompletionAgent(
            service_id=service_id,
            kernel=self.kernel,
            name="TravelAssistant",
            instructions="""你是一个专业的旅游助手。
            你的任务是帮助用户:
            1. 了解可用的旅游目的地
            2. 查询特定目的地的详细信息
            3. 根据预算和偏好推荐最合适的目的地
            
            请用友好、专业的语气回答,并主动询问用户的需求。
            """,
            arguments=KernelArguments(settings=settings)
        )
        
        # 初始化对话历史
        self.chat_history = ChatHistory()
    
    async def chat(self, user_message: str) -> str:
        """与用户对话"""
        # 添加用户消息
        self.chat_history.add_user_message(user_message)
        
        # 获取 Agent 响应
        full_response = ""
        async for content in self.agent.invoke_stream(self.chat_history):
            if hasattr(content, 'content') and content.content:
                full_response += content.content
        
        return full_response.strip()
    
    async def reset(self):
        """重置对话历史"""
        self.chat_history = ChatHistory()
```

### 步骤 3: 创建前端界面

创建 `app.py` (使用 Chainlit):

```python
import chainlit as cl
import asyncio
from agents.travel_agent import TravelAgent

# 全局变量存储 agent
travel_agent = None

@cl.on_chat_start
async def start():
    """聊天开始时初始化"""
    global travel_agent
    travel_agent = TravelAgent()
    
    # 发送欢迎消息
    await cl.Message(
        content="""🌍 欢迎使用智能旅游助手!

我可以帮你:
✈️ 查看可用的旅游目的地
🔍 了解特定地点的详细信息
💡 根据你的预算和偏好推荐最佳目的地

请告诉我你想去哪里,或者让我帮你推荐! 😊
"""
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """处理用户消息"""
    global travel_agent
    
    # 显示加载状态
    msg = cl.Message(content="")
    await msg.send()
    
    # 获取 Agent 响应
    response = await travel_agent.chat(message.content)
    
    # 更新消息内容
    msg.content = response
    await msg.update()

@cl.on_chat_end
async def end():
    """聊天结束"""
    await cl.Message(content="感谢使用智能旅游助手,祝你旅途愉快! 👋").send()
```

### 步骤 4: 运行应用

```bash
# 在终端运行
chainlit run app.py -w
```

浏览器会自动打开 `http://localhost:8000`,你就可以开始与旅游助手对话了!

---

## 🔧 五大核心模块详解

### 1️⃣ Tools (工具) - 扩展 AI 能力

**最佳实践**:

```python
# ✅ 好的工具设计
@kernel_function(description="清晰描述工具的功能")
def good_tool(
    self,
    param: Annotated[str, "详细描述参数的含义和格式"]
) -> Annotated[str, "描述返回值的格式"]:
    # 1. 验证输入
    # 2. 执行操作
    # 3. 返回结构化结果
    pass

# ❌ 不好的工具设计
def bad_tool(param):  # 缺少类型注解和描述
    return result  # 返回格式不明确
```

**工具分类**:

1. **数据检索工具**: 查询数据库、API
2. **数据处理工具**: 计算、转换、分析
3. **外部服务工具**: 发送邮件、调用第三方API

### 2️⃣ Agent (代理) - 智能决策中心

**Agent 设计模式**:

```python
class SpecializedAgent:
    """专门化的 Agent"""
    
    def __init__(self, role: str, tools: list, instructions: str):
        self.role = role
        self.tools = tools
        self.instructions = instructions
        self.memory = []
    
    async def execute_task(self, task: str):
        """执行任务"""
        # 1. 理解任务
        # 2. 选择合适的工具
        # 3. 执行并返回结果
        pass
    
    def update_memory(self, interaction):
        """更新记忆"""
        self.memory.append(interaction)
```

**多 Agent 协作**:

```python
class AgentOrchestrator:
    """Agent 协调器"""
    
    def __init__(self):
        self.agents = {
            "researcher": ResearchAgent(),
            "writer": WriterAgent(),
            "reviewer": ReviewAgent()
        }
    
    async def coordinate(self, task: str):
        """协调多个 Agent 完成任务"""
        # 1. 研究 Agent 收集信息
        research = await self.agents["researcher"].execute(task)
        
        # 2. 写作 Agent 生成内容
        draft = await self.agents["writer"].execute(research)
        
        # 3. 审查 Agent 检查质量
        final = await self.agents["reviewer"].execute(draft)
        
        return final
```

### 3️⃣ Plan (规划) - 任务分解与执行

**创建规划器** `planners/task_planner.py`:

```python
from pydantic import BaseModel
from enum import Enum
from typing import List
import json

class AgentType(str, Enum):
    """Agent 类型枚举"""
    FLIGHT = "flight_booking"
    HOTEL = "hotel_booking"
    CAR = "car_rental"
    ACTIVITIES = "activities_booking"

class SubTask(BaseModel):
    """子任务模型"""
    task_details: str
    assigned_agent: AgentType
    priority: int = 1
    dependencies: List[str] = []

class TravelPlan(BaseModel):
    """旅行计划模型"""
    main_task: str
    subtasks: List[SubTask]
    estimated_time: str

class TaskPlanner:
    """任务规划器"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def create_plan(self, user_request: str) -> TravelPlan:
        """创建执行计划"""
        
        # 系统提示词
        system_prompt = """你是一个任务规划专家。
        根据用户请求,将任务分解为可执行的子任务。
        
        可用的 Agent 类型:
        - flight_booking: 预订航班
        - hotel_booking: 预订酒店
        - car_rental: 租车服务
        - activities_booking: 预订活动
        
        返回 JSON 格式的计划。
        """
        
        # 调用 LLM 生成计划
        response = await self.llm_client.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_request}
            ],
            response_format={"type": "json_object"}
        )
        
        # 解析并验证计划
        plan_data = json.loads(response.content)
        plan = TravelPlan.model_validate(plan_data)
        
        return plan
    
    async def execute_plan(self, plan: TravelPlan, agents: dict):
        """执行计划"""
        results = {}
        
        # 按优先级排序
        sorted_tasks = sorted(plan.subtasks, key=lambda x: x.priority)
        
        for subtask in sorted_tasks:
            # 检查依赖是否完成
            if self._check_dependencies(subtask, results):
                # 获取对应的 Agent
                agent = agents.get(subtask.assigned_agent)
                
                # 执行任务
                result = await agent.execute(subtask.task_details)
                results[subtask.task_details] = result
        
        return results
    
    def _check_dependencies(self, subtask: SubTask, completed: dict) -> bool:
        """检查依赖是否完成"""
        for dep in subtask.dependencies:
            if dep not in completed:
                return False
        return True

# 使用示例
async def demo_planning():
    planner = TaskPlanner(llm_client)
    
    # 创建计划
    plan = await planner.create_plan(
        "我想从北京去巴黎玩5天,预算中等,喜欢艺术和美食"
    )
    
    print("生成的计划:")
    print(f"主任务: {plan.main_task}")
    print("\n子任务:")
    for i, subtask in enumerate(plan.subtasks, 1):
        print(f"{i}. [{subtask.assigned_agent}] {subtask.task_details}")
```

### 4️⃣ Ask (询问) - 与 LLM 交互

**不同的询问模式**:

```python
class LLMInteraction:
    """LLM 交互管理器"""
    
    def __init__(self, client):
        self.client = client
    
    # 1. 简单询问
    async def simple_ask(self, question: str) -> str:
        """单次询问"""
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message.content
    
    # 2. 上下文询问
    async def contextual_ask(self, messages: list) -> str:
        """带上下文的询问"""
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content
    
    # 3. 流式询问
    async def streaming_ask(self, question: str):
        """流式响应"""
        stream = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}],
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    # 4. 结构化询问
    async def structured_ask(self, question: str, schema: type) -> dict:
        """返回结构化数据"""
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

# 使用示例
async def demo_ask_patterns():
    llm = LLMInteraction(client)
    
    # 简单询问
    answer = await llm.simple_ask("什么是 AI Agent?")
    print(f"回答: {answer}")
    
    # 流式输出
    print("\n流式输出:")
    async for chunk in llm.streaming_ask("介绍一下巴黎"):
        print(chunk, end="", flush=True)
    
    # 结构化输出
    data = await llm.structured_ask(
        "生成一个包含name, age, city的JSON",
        schema=dict
    )
    print(f"\n结构化数据: {data}")
```

### 5️⃣ MCP (Model Context Protocol) - 标准化连接

**实现 MCP 服务器**:

创建 `mcp/github_mcp.py`:

```python
import os
from typing import Dict, List, Any
import requests

class GitHubMCPServer:
    """GitHub MCP 服务器"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def list_resources(self) -> List[Dict]:
        """列出可用资源"""
        return [
            {
                "uri": "github://repos",
                "name": "用户仓库列表",
                "description": "获取用户的所有 GitHub 仓库"
            },
            {
                "uri": "github://repo/{owner}/{repo}",
                "name": "仓库详情",
                "description": "获取特定仓库的详细信息"
            },
            {
                "uri": "github://languages/{owner}/{repo}",
                "name": "编程语言",
                "description": "获取仓库使用的编程语言"
            }
        ]
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """读取资源"""
        if uri == "github://repos":
            return self._get_user_repos()
        elif uri.startswith("github://repo/"):
            parts = uri.split("/")
            owner, repo = parts[3], parts[4]
            return self._get_repo_info(owner, repo)
        elif uri.startswith("github://languages/"):
            parts = uri.split("/")
            owner, repo = parts[3], parts[4]
            return self._get_repo_languages(owner, repo)
        else:
            raise ValueError(f"未知的资源 URI: {uri}")
    
    def _get_user_repos(self) -> Dict:
        """获取用户仓库"""
        response = requests.get(
            f"{self.base_url}/user/repos",
            headers=self.headers
        )
        repos = response.json()
        
        return {
            "repos": [
                {
                    "name": repo["name"],
                    "description": repo["description"],
                    "stars": repo["stargazers_count"],
                    "language": repo["language"]
                }
                for repo in repos
            ]
        }
    
    def _get_repo_info(self, owner: str, repo: str) -> Dict:
        """获取仓库详情"""
        response = requests.get(
            f"{self.base_url}/repos/{owner}/{repo}",
            headers=self.headers
        )
        return response.json()
    
    def _get_repo_languages(self, owner: str, repo: str) -> Dict:
        """获取仓库语言"""
        response = requests.get(
            f"{self.base_url}/repos/{owner}/{repo}/languages",
            headers=self.headers
        )
        return response.json()

class MCPClient:
    """MCP 客户端"""
    
    def __init__(self):
        self.servers = {}
    
    def register_server(self, name: str, server):
        """注册 MCP 服务器"""
        self.servers[name] = server
    
    def list_all_resources(self) -> Dict[str, List]:
        """列出所有服务器的资源"""
        resources = {}
        for name, server in self.servers.items():
            resources[name] = server.list_resources()
        return resources
    
    def fetch_resource(self, server_name: str, uri: str) -> Any:
        """从指定服务器获取资源"""
        if server_name not in self.servers:
            raise ValueError(f"未找到服务器: {server_name}")
        
        server = self.servers[server_name]
        return server.read_resource(uri)

# 在 Agent 中集成 MCP
class MCPEnabledAgent:
    """支持 MCP 的 Agent"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.agent = self._create_agent()
    
    def _create_agent(self):
        # 创建带有 MCP 工具的 Agent
        @kernel_function(description="从 MCP 服务器获取资源")
        def fetch_mcp_resource(
            server: Annotated[str, "MCP 服务器名称"],
            uri: Annotated[str, "资源 URI"]
        ) -> str:
            result = self.mcp_client.fetch_resource(server, uri)
            return json.dumps(result, ensure_ascii=False)
        
        # 将工具添加到 Agent
        # ...
        return agent

# 使用示例
async def demo_mcp():
    # 创建 MCP 客户端
    mcp_client = MCPClient()
    
    # 注册 GitHub MCP 服务器
    github_server = GitHubMCPServer(os.getenv("GITHUB_TOKEN"))
    mcp_client.register_server("github", github_server)
    
    # 创建支持 MCP 的 Agent
    agent = MCPEnabledAgent(mcp_client)
    
    # Agent 可以通过 MCP 访问 GitHub 数据
    response = await agent.chat(
        "请列出我的 GitHub 仓库,并告诉我哪个项目最受欢迎"
    )
    print(response)
```

---

## 🎨 完整项目实现

### 高级旅游助手 - 多 Agent 系统

**项目结构**:
```
advanced-travel-assistant/
├── agents/
│   ├── flight_agent.py      # 航班搜索 Agent
│   ├── hotel_agent.py       # 酒店预订 Agent
│   ├── activity_agent.py    # 活动推荐 Agent
│   └── coordinator_agent.py # 协调器 Agent
├── tools/
│   ├── flight_tools.py
│   ├── hotel_tools.py
│   └── weather_tools.py
├── planners/
│   └── travel_planner.py
├── mcp/
│   └── travel_mcp.py
├── app.py
└── .env
```

**完整实现** `app.py`:

```python
import chainlit as cl
from agents.coordinator_agent import CoordinatorAgent
from agents.flight_agent import FlightAgent
from agents.hotel_agent import HotelAgent
from agents.activity_agent import ActivityAgent
from planners.travel_planner import TravelPlanner
from mcp.travel_mcp import TravelMCPClient

# 全局变量
coordinator = None

@cl.on_chat_start
async def start():
    """初始化多 Agent 系统"""
    global coordinator
    
    # 1. 创建专门化的 Agent
    flight_agent = FlightAgent()
    hotel_agent = HotelAgent()
    activity_agent = ActivityAgent()
    
    # 2. 创建规划器
    planner = TravelPlanner()
    
    # 3. 创建 MCP 客户端
    mcp_client = TravelMCPClient()
    
    # 4. 创建协调器
    coordinator = CoordinatorAgent(
        agents={
            "flight": flight_agent,
            "hotel": hotel_agent,
            "activity": activity_agent
        },
        planner=planner,
        mcp_client=mcp_client
    )
    
    # 欢迎消息
    await cl.Message(content="""🌟 欢迎使用高级旅游助手!

我是一个多 Agent 协作系统,可以帮你:
✈️ 搜索和预订航班
🏨 查找最佳酒店
🎭 推荐当地活动
📋 制定完整的旅行计划

告诉我你的旅行想法,我会为你规划一切! 😊
""").send()

@cl.on_message
async def main(message: cl.Message):
    """处理用户消息"""
    global coordinator
    
    # 创建思考状态消息
    thinking_msg = cl.Message(content="🤔 正在思考...")
    await thinking_msg.send()
    
    # 协调器处理请求
    result = await coordinator.process_request(message.content)
    
    # 更新消息
    thinking_msg.content = result
    await thinking_msg.update()
    
    # 如果生成了计划,显示计划详情
    if result.get("plan"):
        plan_msg = await cl.Message(
            content=f"""📋 **旅行计划已生成**

**主要任务**: {result['plan'].main_task}

**执行步骤**:
"""
        ).send()
        
        for i, subtask in enumerate(result['plan'].subtasks, 1):
            plan_msg.content += f"\n{i}. [{subtask.assigned_agent}] {subtask.task_details}"
        
        await plan_msg.update()

@cl.on_settings_update
async def settings_update(settings):
    """更新设置"""
    # 可以让用户自定义偏好
    pass
```

---

## 🧪 测试与优化

### 测试用例

创建 `tests/test_agents.py`:

```python
import pytest
from agents.travel_agent import TravelAgent

@pytest.mark.asyncio
async def test_destination_query():
    """测试目的地查询"""
    agent = TravelAgent()
    
    response = await agent.chat("巴黎现在可以预订吗?")
    
    assert "巴黎" in response
    assert "可预订" in response or "已满" in response

@pytest.mark.asyncio
async def test_recommendation():
    """测试推荐功能"""
    agent = TravelAgent()
    
    response = await agent.chat("推荐一个预算中等、喜欢美食的目的地")
    
    assert len(response) > 0
    # 应该包含推荐的地点

@pytest.mark.asyncio
async def test_multi_turn_conversation():
    """测试多轮对话"""
    agent = TravelAgent()
    
    # 第一轮
    r1 = await agent.chat("有哪些目的地?")
    assert len(r1) > 0
    
    # 第二轮 - 测试上下文记忆
    r2 = await agent.chat("第一个怎么样?")
    assert len(r2) > 0
```

### 性能优化

```python
# 1. 缓存机制
from functools import lru_cache
import hashlib

class CachedAgent:
    """带缓存的 Agent"""
    
    def __init__(self):
        self.cache = {}
    
    def _get_cache_key(self, message: str) -> str:
        """生成缓存键"""
        return hashlib.md5(message.encode()).hexdigest()
    
    async def chat(self, message: str) -> str:
        """带缓存的对话"""
        cache_key = self._get_cache_key(message)
        
        # 检查缓存
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 调用 Agent
        response = await self._real_chat(message)
        
        # 存入缓存
        self.cache[cache_key] = response
        
        return response

# 2. 并行执行
import asyncio

async def parallel_agent_execution(tasks: list):
    """并行执行多个 Agent 任务"""
    results = await asyncio.gather(*tasks)
    return results

# 使用示例
async def demo_parallel():
    agent = TravelAgent()
    
    tasks = [
        agent.chat("查询巴黎"),
        agent.chat("查询东京"),
        agent.chat("查询纽约")
    ]
    
    results = await parallel_agent_execution(tasks)
    return results
```

### 监控和日志

```python
import logging
from datetime import datetime

class AgentMonitor:
    """Agent 监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger("AgentMonitor")
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0
        }
    
    async def track_request(self, agent_name: str, request: str):
        """跟踪请求"""
        start_time = datetime.now()
        
        try:
            self.metrics["total_requests"] += 1
            
            # 执行请求
            result = await self._execute_request(agent_name, request)
            
            # 记录成功
            self.metrics["successful_requests"] += 1
            
            # 计算响应时间
            elapsed = (datetime.now() - start_time).total_seconds()
            self._update_avg_response_time(elapsed)
            
            # 日志
            self.logger.info(
                f"Agent: {agent_name} | "
                f"Request: {request[:50]}... | "
                f"Time: {elapsed:.2f}s | "
                f"Status: SUCCESS"
            )
            
            return result
            
        except Exception as e:
            self.metrics["failed_requests"] += 1
            self.logger.error(f"Agent: {agent_name} | Error: {str(e)}")
            raise
    
    def get_metrics(self) -> dict:
        """获取监控指标"""
        return {
            **self.metrics,
            "success_rate": (
                self.metrics["successful_requests"] / 
                self.metrics["total_requests"] * 100
                if self.metrics["total_requests"] > 0 
                else 0
            )
        }
```

---

## 🚀 部署建议

### 本地开发
```bash
# 运行 Chainlit 应用
chainlit run app.py -w
```

### Docker 部署
创建 `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
```

### 云部署 (Azure)
```bash
# 使用 Azure Container Apps
az containerapp up \
  --name travel-agent \
  --resource-group my-rg \
  --location eastus \
  --environment my-env \
  --image myregistry.azurecr.io/travel-agent:latest \
  --target-port 8000 \
  --ingress external
```

---

## 📚 学习资源

### 推荐阅读
1. 本项目的 README 文件
2. `01-intro-to-ai-agents/` - AI Agents 基础
3. `04-tool-use/` - 工具使用详解
4. `07-planning-design/` - 规划设计模式
5. `11-mcp/` - MCP 协议详解

### 相关链接
- [Semantic Kernel 文档](https://learn.microsoft.com/semantic-kernel/)
- [Azure AI Agent Service](https://learn.microsoft.com/azure/ai-services/agents/)
- [AutoGen 框架](https://microsoft.github.io/autogen/)
- [Chainlit 文档](https://docs.chainlit.io/)

---

## ✅ 检查清单

开发第一个 AI 工具前,确保:

- [ ] 已安装所有必要的依赖
- [ ] 已配置环境变量 (.env)
- [ ] 理解 Agent、Tool、Plan 的概念
- [ ] 熟悉 Cursor 的基本操作
- [ ] 已测试 API 连接 (GitHub Models 或 Azure OpenAI)

开发完成后:
- [ ] 工具函数有清晰的描述和类型注解
- [ ] Agent 指令明确且易于理解
- [ ] 已实现错误处理
- [ ] 已添加日志记录
- [ ] 已进行基本测试
- [ ] 前端界面友好易用

---

## 🎯 下一步

1. **扩展工具集**: 添加更多自定义工具
2. **多 Agent 协作**: 实现多个 Agent 的协同工作
3. **记忆系统**: 添加长期记忆能力
4. **用户个性化**: 根据用户偏好自动调整
5. **生产部署**: 部署到云端供实际使用

祝你开发顺利! 🎉
