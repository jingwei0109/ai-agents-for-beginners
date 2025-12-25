# 🌍 智能旅游助手 - 你的第一个 AI 业务工具

这是一个完整的 AI Agent 应用示例,展示了如何使用 **Agents**、**Tools**、**Plan**、**Ask** 和 **MCP** 构建实用的 AI 业务工具。

## ✨ 功能特性

- 🤖 **智能 Agent**: 基于 Semantic Kernel 的 AI 代理
- 🛠️ **工具集成**: 自定义工具函数(Tools)
- 💬 **自然对话**: 支持多轮对话和上下文记忆
- 🎨 **友好界面**: 基于 Chainlit 的聊天界面
- 🔄 **自动规划**: Agent 自动选择合适的工具

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd my-first-ai-tool

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件,填入你的 GitHub Token
# 获取 Token: https://github.com/settings/tokens
```

**.env 配置示例:**
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### 3. 运行应用

```bash
# 启动 Chainlit 应用
chainlit run app.py -w
```

浏览器会自动打开 `http://localhost:8000` 🎉

### 4. 测试 Agent (可选)

```bash
# 在终端测试 Agent 功能
python agents/travel_agent.py
```

## 📁 项目结构

```
my-first-ai-tool/
├── agents/                    # Agent 定义
│   ├── __init__.py
│   └── travel_agent.py       # 旅游助手 Agent
├── tools/                     # 工具函数
│   ├── __init__.py
│   └── travel_tools.py       # 旅游相关工具
├── planners/                  # 规划器(高级功能)
├── mcp/                       # MCP 集成(高级功能)
├── tests/                     # 测试文件
├── app.py                     # Chainlit 前端应用
├── .env.example              # 环境变量模板
├── requirements.txt          # 依赖列表
└── README.md                 # 本文件
```

## 🎯 使用示例

启动应用后,你可以尝试以下对话:

1. **查询所有目的地**
   ```
   有哪些目的地可以选择?
   ```

2. **查询特定地点**
   ```
   巴黎现在可以预订吗?
   Tokyo怎么样?
   ```

3. **获取智能推荐**
   ```
   推荐一个预算中等,喜欢美食的地方
   我想去海滩度假,预算不高
   ```

## 🧠 核心概念

### Agent (代理)
- **定义**: 能够感知、决策并执行动作的 AI 系统
- **实现**: `agents/travel_agent.py`
- **特点**: 自动选择工具、保持对话上下文

### Tools (工具)
- **定义**: Agent 可以调用的函数
- **实现**: `tools/travel_tools.py`
- **包含**:
  - `get_destinations()` - 获取目的地列表
  - `check_destination_availability()` - 查询可用性
  - `recommend_destination()` - 智能推荐

### Ask (询问)
- **定义**: 与 LLM 交互获取响应
- **实现**: 通过 Semantic Kernel 的 ChatCompletionAgent
- **特点**: 支持流式输出、上下文管理

### Plan (规划)
- **定义**: 将复杂任务分解为子任务
- **当前**: Agent 自动规划工具调用
- **扩展**: 可在 `planners/` 中实现更复杂的规划逻辑

### MCP (Model Context Protocol)
- **定义**: 标准化的外部数据/工具连接协议
- **扩展**: 可在 `mcp/` 中实现 MCP 服务器

## 🔧 自定义扩展

### 添加新工具

在 `tools/travel_tools.py` 中添加新函数:

```python
@kernel_function(description="你的工具描述")
def your_new_tool(
    self,
    param: Annotated[str, "参数描述"]
) -> Annotated[str, "返回值描述"]:
    # 你的逻辑
    return result
```

### 修改 Agent 行为

编辑 `agents/travel_agent.py` 中的 `instructions` 字段:

```python
instructions="""
你的自定义指令...
"""
```

### 自定义界面

修改 `app.py` 中的欢迎消息和样式。

## 🧪 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_agents.py -v
```

## 📚 学习资源

- 📖 [完整开发指南](../前端AI业务工具开发实操指南.md)
- 🎓 [AI Agents 课程](/workspace/README.md)
- 🔗 [Semantic Kernel 文档](https://learn.microsoft.com/semantic-kernel/)
- 🔗 [Chainlit 文档](https://docs.chainlit.io/)

## ❓ 常见问题

### Q: Agent 没有响应?
A: 检查 .env 文件中的 GITHUB_TOKEN 是否正确配置

### Q: 如何切换到 Azure OpenAI?
A: 修改 `agents/travel_agent.py` 中的客户端初始化代码

### Q: 如何添加更多目的地?
A: 编辑 `tools/travel_tools.py` 中的数据字典

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License

---

## 🎉 下一步

1. ✅ 成功运行基础应用
2. 🔨 添加自定义工具和功能
3. 🚀 实现多 Agent 协作
4. 📊 添加数据持久化
5. 🌐 部署到生产环境

祝你开发顺利! 有问题随时查看[完整指南](../前端AI业务工具开发实操指南.md) 💪
