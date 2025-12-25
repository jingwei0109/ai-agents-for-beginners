"""
智能旅游助手 - Chainlit 前端应用
这是一个完整的 AI 应用,展示了 Agents、Tools、Ask 的集成
"""

import chainlit as cl
from agents.travel_agent import TravelAgent

# 全局变量存储 agent
travel_agent = None


@cl.on_chat_start
async def start():
    """聊天开始时初始化"""
    global travel_agent
    
    # 显示加载消息
    loading_msg = cl.Message(content="🚀 正在初始化智能旅游助手...")
    await loading_msg.send()
    
    try:
        # 创建 Travel Agent
        travel_agent = TravelAgent()
        
        # 更新为欢迎消息
        loading_msg.content = """🌍 欢迎使用智能旅游助手!

我是您的 AI 旅行伙伴,可以帮助您:

✈️ **查看目的地** - 了解所有可选的旅游地点
🔍 **查询详情** - 获取特定目的地的详细信息
💡 **智能推荐** - 根据您的预算和偏好推荐最佳地点

━━━━━━━━━━━━━━━━━━━━━━━━━━

**快速开始:**
• "有哪些目的地?" - 查看所有选项
• "巴黎怎么样?" - 查询特定地点
• "推荐一个预算中等的地方" - 获取推荐

准备好开始您的旅程了吗? 告诉我您想去哪里! 😊
"""
        await loading_msg.update()
        
        # 设置用户会话数据
        cl.user_session.set("agent", travel_agent)
        
    except Exception as e:
        loading_msg.content = f"❌ 初始化失败: {str(e)}\n\n请检查:\n1. .env 文件是否配置正确\n2. GITHUB_TOKEN 是否有效"
        await loading_msg.update()


@cl.on_message
async def main(message: cl.Message):
    """处理用户消息"""
    travel_agent = cl.user_session.get("agent")
    
    if not travel_agent:
        await cl.Message(content="❌ Agent 未初始化,请刷新页面重试").send()
        return
    
    # 创建响应消息
    msg = cl.Message(content="")
    await msg.send()
    
    try:
        # 显示思考状态
        msg.content = "🤔 正在思考..."
        await msg.update()
        
        # 获取 Agent 响应
        response = await travel_agent.chat(message.content)
        
        # 更新消息内容
        msg.content = response if response else "抱歉,我没有理解您的问题。能否换个方式问我?"
        await msg.update()
        
    except Exception as e:
        msg.content = f"❌ 处理请求时出错: {str(e)}\n\n请重试或联系管理员。"
        await msg.update()


@cl.on_chat_end
async def end():
    """聊天结束"""
    await cl.Message(
        content="👋 感谢使用智能旅游助手!\n\n祝您旅途愉快,期待下次再见! ✨"
    ).send()


@cl.action_callback("reset_conversation")
async def on_reset(action: cl.Action):
    """重置对话"""
    travel_agent = cl.user_session.get("agent")
    if travel_agent:
        await travel_agent.reset()
        await cl.Message(content="✅ 对话已重置,让我们重新开始吧!").send()


# 添加自定义操作
@cl.on_chat_start
async def setup_actions():
    """设置自定义操作"""
    actions = [
        cl.Action(
            name="reset_conversation",
            value="reset",
            label="🔄 重置对话",
            description="清空对话历史,重新开始"
        )
    ]
    
    # 显示操作按钮
    # await cl.Message(content="", actions=actions).send()


if __name__ == "__main__":
    # 运行 Chainlit 应用
    # 在终端执行: chainlit run app.py -w
    pass
