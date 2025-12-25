"""
旅游助手 Agent
这是一个智能 AI 代理,可以帮助用户查询和推荐旅游目的地
"""

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
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools.travel_tools import TravelToolsPlugin


class TravelAgent:
    """旅游助手 Agent - 智能旅游规划助手"""
    
    def __init__(self):
        """初始化 Agent"""
        load_dotenv()
        
        # 初始化 OpenAI 客户端 (使用 GitHub Models)
        self.client = AsyncOpenAI(
            api_key=os.getenv("GITHUB_TOKEN"),
            base_url="https://models.inference.ai.azure.com/"
        )
        
        # 创建 Semantic Kernel
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
        
        # 设置函数调用行为 (允许 Agent 自动选择工具)
        settings = self.kernel.get_prompt_execution_settings_from_service_id(
            service_id=service_id
        )
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        
        # 创建 Agent
        self.agent = ChatCompletionAgent(
            service_id=service_id,
            kernel=self.kernel,
            name="智能旅游助手",
            instructions="""你是一个专业且友好的旅游助手 🌍

你的职责:
1. 帮助用户了解可用的旅游目的地
2. 查询特定目的地的详细信息(可用性、特色、天气等)
3. 根据用户的预算和偏好推荐最合适的目的地

你的风格:
• 友好、专业、热情
• 使用表情符号让对话更生动
• 主动询问用户的需求
• 提供详细且有用的信息

当用户询问时,你应该:
1. 理解用户的需求
2. 使用合适的工具获取信息
3. 用清晰、友好的方式呈现结果
4. 主动提供额外的建议

记住: 你的目标是让用户的旅行计划变得简单而美好! ✨
""",
            arguments=KernelArguments(settings=settings)
        )
        
        # 初始化对话历史
        self.chat_history = ChatHistory()
    
    async def chat(self, user_message: str) -> str:
        """
        与用户对话
        
        Args:
            user_message: 用户消息
            
        Returns:
            Agent 的响应
        """
        # 添加用户消息到历史
        self.chat_history.add_user_message(user_message)
        
        # 获取 Agent 响应
        full_response = ""
        async for content in self.agent.invoke_stream(self.chat_history):
            if hasattr(content, 'content') and content.content:
                # 过滤掉函数调用相关的内容
                from semantic_kernel.contents.function_call_content import FunctionCallContent
                from semantic_kernel.contents.function_result_content import FunctionResultContent
                
                is_function_content = any(
                    isinstance(item, (FunctionCallContent, FunctionResultContent))
                    for item in content.items
                )
                
                if not is_function_content and content.content.strip():
                    full_response += content.content
        
        return full_response.strip()
    
    async def reset(self):
        """重置对话历史"""
        self.chat_history = ChatHistory()
        return "✅ 对话历史已重置,让我们重新开始吧!"


# 测试代码
async def test_agent():
    """测试 Agent 功能"""
    agent = TravelAgent()
    
    print("🌍 旅游助手测试")
    print("=" * 50)
    
    # 测试 1: 查询目的地列表
    print("\n测试 1: 查询所有目的地")
    print("-" * 50)
    response = await agent.chat("有哪些目的地可以选择?")
    print(response)
    
    # 测试 2: 查询特定目的地
    print("\n\n测试 2: 查询巴黎")
    print("-" * 50)
    response = await agent.chat("巴黎现在可以预订吗?")
    print(response)
    
    # 测试 3: 推荐目的地
    print("\n\n测试 3: 推荐目的地")
    print("-" * 50)
    response = await agent.chat("我预算中等,喜欢美食,推荐一个地方")
    print(response)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent())
