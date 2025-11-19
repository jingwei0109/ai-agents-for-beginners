"""
使用示例
"""
import asyncio
import os
from client import AIClient
from base import Message


async def example_basic_usage():
    """基础使用示例"""
    print("=" * 50)
    print("基础使用示例")
    print("=" * 50)
    
    # 创建客户端
    client = AIClient(
        provider="openai",
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key"),
        enable_cache=True
    )
    
    # 创建消息
    messages = [
        Message(role="system", content="You are a helpful assistant"),
        Message(role="user", content="What is Python? Answer in one sentence.")
    ]
    
    # 第一次请求
    print("\n第一次请求...")
    response = await client.complete(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    print(f"响应: {response.content}")
    print(f"使用token: {response.usage['total_tokens']}")
    print(f"延迟: {response.latency_ms:.2f}ms")
    print(f"来自缓存: {response.cached}")
    
    # 第二次请求（应该从缓存获取）
    print("\n第二次请求（相同参数）...")
    response = await client.complete(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    print(f"响应: {response.content}")
    print(f"来自缓存: {response.cached}")
    print(f"延迟: {response.latency_ms:.2f}ms")
    
    # 查看统计
    stats = client.get_stats()
    print(f"\n统计信息:")
    print(f"  总请求数: {stats['total_requests']}")
    print(f"  缓存命中: {stats['cache_hits']}")
    print(f"  缓存未命中: {stats['cache_misses']}")
    print(f"  缓存命中率: {stats['cache_hit_rate']:.2%}")


async def example_streaming():
    """流式响应示例"""
    print("\n" + "=" * 50)
    print("流式响应示例")
    print("=" * 50)
    
    client = AIClient(
        provider="openai",
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key")
    )
    
    messages = [
        Message(role="system", content="You are a helpful assistant"),
        Message(role="user", content="Write a short poem about AI.")
    ]
    
    print("\n生成中...")
    async for chunk in client.stream_complete(
        messages=messages,
        model="gpt-4o-mini"
    ):
        print(chunk, end="", flush=True)
    
    print("\n")


async def example_prefetch():
    """预取功能示例"""
    print("\n" + "=" * 50)
    print("预取功能示例")
    print("=" * 50)
    
    client = AIClient(
        provider="openai",
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key"),
        enable_cache=True
    )
    
    # 准备多个请求
    messages_list = [
        [Message(role="user", content="What is AI? Answer in one sentence.")],
        [Message(role="user", content="What is Machine Learning? Answer in one sentence.")],
        [Message(role="user", content="What is Deep Learning? Answer in one sentence.")]
    ]
    
    print("\n预取中...")
    await client.prefetch(
        messages_list=messages_list,
        model="gpt-4o-mini"
    )
    print("预取完成！")
    
    # 现在这些请求应该都能从缓存获取
    print("\n从缓存获取预取的结果...")
    for i, messages in enumerate(messages_list, 1):
        response = await client.complete(
            messages=messages,
            model="gpt-4o-mini"
        )
        print(f"\n问题 {i}: {messages[0].content}")
        print(f"答案: {response.content}")
        print(f"来自缓存: {response.cached}")
    
    # 统计
    stats = client.get_stats()
    print(f"\n缓存命中率: {stats['cache_hit_rate']:.2%}")


async def example_multiple_providers():
    """多提供商示例"""
    print("\n" + "=" * 50)
    print("多提供商示例")
    print("=" * 50)
    
    messages = [
        Message(role="user", content="Say 'Hello from' and your name!")
    ]
    
    providers_config = [
        {
            "name": "OpenAI",
            "provider": "openai",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4o-mini"
        },
        {
            "name": "Anthropic",
            "provider": "anthropic",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "model": "claude-3-5-sonnet-20241022"
        }
    ]
    
    for config in providers_config:
        if not config["api_key"]:
            print(f"\n跳过 {config['name']}（未配置API密钥）")
            continue
            
        print(f"\n测试 {config['name']}...")
        try:
            client = AIClient(
                provider=config["provider"],
                api_key=config["api_key"]
            )
            
            response = await client.complete(
                messages=messages,
                model=config["model"]
            )
            
            print(f"响应: {response.content}")
            print(f"延迟: {response.latency_ms:.2f}ms")
            
        except Exception as e:
            print(f"错误: {e}")


async def example_with_config():
    """使用配置文件示例"""
    print("\n" + "=" * 50)
    print("使用配置文件示例")
    print("=" * 50)
    
    from config import ClientConfig
    
    # 从环境变量创建配置
    config = ClientConfig.from_env("openai")
    client = AIClient(**config.to_client_kwargs())
    
    messages = [
        Message(role="user", content="Hello!")
    ]
    
    response = await client.complete(
        messages=messages,
        model="gpt-4o-mini"
    )
    
    print(f"响应: {response.content}")


async def example_helper_methods():
    """辅助方法示例"""
    print("\n" + "=" * 50)
    print("辅助方法示例")
    print("=" * 50)
    
    client = AIClient(
        provider="openai",
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key")
    )
    
    # 使用create_message
    msg = client.create_message("user", "What is AI?")
    print(f"创建的消息: {msg}")
    
    # 使用create_messages批量创建
    messages = client.create_messages(
        ("system", "You are a helpful assistant"),
        ("user", "Hello!"),
        ("assistant", "Hi! How can I help you?"),
        ("user", "Tell me a joke")
    )
    
    print(f"\n批量创建了 {len(messages)} 条消息")
    
    response = await client.complete(
        messages=messages,
        model="gpt-4o-mini"
    )
    
    print(f"\n响应: {response.content}")


async def main():
    """运行所有示例"""
    try:
        await example_basic_usage()
        await example_streaming()
        await example_prefetch()
        await example_helper_methods()
        # await example_multiple_providers()  # 需要多个API密钥
        # await example_with_config()  # 需要环境变量配置
        
    except Exception as e:
        print(f"\n错误: {e}")
        print("请确保已设置正确的API密钥")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
