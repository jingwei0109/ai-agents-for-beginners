"""
基础使用示例
演示如何使用AI Gateway的基本功能
"""

import asyncio
import os
from dotenv import load_dotenv

# 导入AI Gateway
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai_gateway import (
    AIGateway,
    OpenAIProvider,
    GitHubModelsProvider,
    Message,
    MessageRole,
    CacheManager
)


async def basic_example():
    """基础使用示例"""
    print("=" * 60)
    print("AI Gateway - 基础使用示例")
    print("=" * 60)
    
    # 加载环境变量
    load_dotenv()
    
    # 1. 创建AI Gateway实例
    gateway = AIGateway(
        enable_cache=True,
        enable_retry=True,
        max_retries=3
    )
    
    # 2. 添加服务提供商
    # 方式A: 使用GitHub Models (免费)
    if os.getenv("GITHUB_TOKEN"):
        github_provider = GitHubModelsProvider(
            api_key=os.getenv("GITHUB_TOKEN")
        )
        gateway.add_provider(
            name="github",
            provider=github_provider,
            priority=1,
            weight=1
        )
        print("✅ GitHub Models provider 已添加")
    
    # 方式B: 使用OpenAI
    if os.getenv("OPENAI_API_KEY"):
        openai_provider = OpenAIProvider(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        gateway.add_provider(
            name="openai",
            provider=openai_provider,
            priority=2,
            weight=1
        )
        print("✅ OpenAI provider 已添加")
    
    print()
    
    # 3. 准备消息
    messages = [
        Message(
            role=MessageRole.SYSTEM,
            content="你是一个helpful assistant"
        ),
        Message(
            role=MessageRole.USER,
            content="请用一句话介绍什么是AI Gateway"
        )
    ]
    
    # 4. 发送请求
    print("📤 发送请求...")
    try:
        response = await gateway.complete(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.7
        )
        
        print(f"\n✅ 收到响应:")
        print(f"   Provider: {response.provider.value}")
        print(f"   Model: {response.model}")
        print(f"   Latency: {response.latency_ms:.2f}ms")
        print(f"   Cached: {response.cached}")
        print(f"   Tokens: {response.usage['total_tokens']}")
        print(f"\n📝 内容:")
        print(f"   {response.content}")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
    
    print()
    
    # 5. 再次发送相同请求（测试缓存）
    print("📤 再次发送相同请求（测试缓存）...")
    try:
        response2 = await gateway.complete(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.7
        )
        
        print(f"\n✅ 收到响应:")
        print(f"   Cached: {response2.cached}")
        print(f"   Latency: {response2.latency_ms:.2f}ms")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
    
    print()
    
    # 6. 查看统计信息
    stats = await gateway.get_stats()
    print("📊 统计信息:")
    print(f"   总请求数: {stats['gateway']['total_requests']}")
    print(f"   缓存命中: {stats['gateway']['cache_hits']}")
    print(f"   缓存未命中: {stats['gateway']['cache_misses']}")
    print(f"   缓存命中率: {stats['cache']['hit_rate']:.2%}")


async def stream_example():
    """流式输出示例"""
    print("\n" + "=" * 60)
    print("AI Gateway - 流式输出示例")
    print("=" * 60)
    
    load_dotenv()
    
    gateway = AIGateway()
    
    # 添加提供商
    if os.getenv("GITHUB_TOKEN"):
        gateway.add_provider(
            "github",
            GitHubModelsProvider(api_key=os.getenv("GITHUB_TOKEN"))
        )
    
    messages = [
        Message(
            role=MessageRole.USER,
            content="请写一首关于AI的五言绝句"
        )
    ]
    
    print("\n📤 开始流式输出...\n")
    
    try:
        async for chunk in gateway.complete_stream(
            messages=messages,
            model="gpt-4o-mini"
        ):
            print(chunk, end="", flush=True)
        
        print("\n\n✅ 流式输出完成")
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")


async def fallback_example():
    """Fallback示例"""
    print("\n" + "=" * 60)
    print("AI Gateway - Fallback示例")
    print("=" * 60)
    
    load_dotenv()
    
    gateway = AIGateway()
    
    # 添加多个提供商（不同优先级）
    if os.getenv("GITHUB_TOKEN"):
        gateway.add_provider(
            "github_primary",
            GitHubModelsProvider(api_key=os.getenv("GITHUB_TOKEN")),
            priority=1
        )
        print("✅ 主提供商: GitHub Models (优先级 1)")
    
    if os.getenv("OPENAI_API_KEY"):
        gateway.add_provider(
            "openai_backup",
            OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY")),
            priority=2
        )
        print("✅ 备用提供商: OpenAI (优先级 2)")
    
    messages = [
        Message(
            role=MessageRole.USER,
            content="Hello, AI!"
        )
    ]
    
    print("\n📤 发送请求（会自动选择优先级最高的提供商）...")
    
    try:
        response = await gateway.complete(
            messages=messages,
            model="gpt-4o-mini"
        )
        
        print(f"\n✅ 使用的提供商: {response.provider.value}")
        print(f"   响应: {response.content[:100]}...")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")


async def main():
    """主函数"""
    try:
        # 运行基础示例
        await basic_example()
        
        # 运行流式示例
        await stream_example()
        
        # 运行Fallback示例
        await fallback_example()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  程序被中断")


if __name__ == "__main__":
    asyncio.run(main())
