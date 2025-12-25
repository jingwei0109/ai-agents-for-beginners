"""
旅游助手 Agent 测试
"""

import pytest
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.travel_agent import TravelAgent


@pytest.mark.asyncio
async def test_agent_initialization():
    """测试 Agent 初始化"""
    agent = TravelAgent()
    assert agent is not None
    assert agent.agent is not None
    assert agent.chat_history is not None


@pytest.mark.asyncio
async def test_get_destinations():
    """测试查询目的地列表"""
    agent = TravelAgent()
    
    response = await agent.chat("有哪些目的地可以选择?")
    
    # 验证响应包含目的地信息
    assert len(response) > 0
    # 应该包含至少一个目的地名称
    assert any(city in response for city in ["Paris", "Tokyo", "Bali", "Barcelona", "New York"])


@pytest.mark.asyncio
async def test_check_availability():
    """测试查询特定目的地"""
    agent = TravelAgent()
    
    response = await agent.chat("巴黎现在可以预订吗?")
    
    # 验证响应
    assert len(response) > 0
    assert "巴黎" in response or "Paris" in response


@pytest.mark.asyncio
async def test_recommendation():
    """测试推荐功能"""
    agent = TravelAgent()
    
    response = await agent.chat("推荐一个预算中等、喜欢美食的目的地")
    
    # 验证响应包含推荐信息
    assert len(response) > 0


@pytest.mark.asyncio
async def test_multi_turn_conversation():
    """测试多轮对话"""
    agent = TravelAgent()
    
    # 第一轮: 查询列表
    response1 = await agent.chat("有哪些目的地?")
    assert len(response1) > 0
    
    # 第二轮: 询问具体信息
    response2 = await agent.chat("第一个怎么样?")
    assert len(response2) > 0
    
    # 验证 Agent 保持了上下文
    assert len(agent.chat_history.messages) >= 4  # 至少2轮对话


@pytest.mark.asyncio
async def test_reset_conversation():
    """测试重置对话"""
    agent = TravelAgent()
    
    # 进行一些对话
    await agent.chat("你好")
    initial_length = len(agent.chat_history.messages)
    
    # 重置
    await agent.reset()
    
    # 验证历史已清空
    assert len(agent.chat_history.messages) == 0


@pytest.mark.asyncio
async def test_invalid_destination():
    """测试查询不存在的目的地"""
    agent = TravelAgent()
    
    response = await agent.chat("查询火星的信息")
    
    # 应该能够优雅地处理
    assert len(response) > 0


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])
