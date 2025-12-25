"""
高级使用示例
演示负载均衡、健康检查、自定义缓存等高级功能
"""

import asyncio
import os
from dotenv import load_dotenv

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai_gateway import (
    AIGateway,
    OpenAIProvider,
    GitHubModelsProvider,
    Message,
    MessageRole,
    CacheManager,
    MemoryCacheBackend
)


async def load_balancing_example():
    """负载均衡示例"""
    print("=" * 60)
    print("负载均衡示例")
    print("=" * 60)
    
    load_dotenv()
    
    gateway = AIGateway()
    
    # 添加多个相同优先级但不同权重的提供商
    if os.getenv("GITHUB_TOKEN"):
        gateway.add_provider(
            "github_1",
            GitHubModelsProvider(api_key=os.getenv("GITHUB_TOKEN")),
            priority=1,
            weight=3  # 权重3
        )
        gateway.add_provider(
            "github_2",
            GitHubModelsProvider(api_key=os.getenv("GITHUB_TOKEN")),
            priority=1,
            weight=1  # 权重1
        )
        print("✅ 已添加2个提供商 (权重比 3:1)")
    
    # 发送多个请求，观察负载分布
    provider_usage = {}
    
    messages = [
        Message(role=MessageRole.USER, content=f"Say hello {i}")
        for i in range(10)
    ]
    
    print("\n📤 发送10个请求...")
    
    for i, msg in enumerate(messages, 1):
        try:
            response = await gateway.complete(
                messages=[msg],
                model="gpt-4o-mini",
                use_cache=False  # 禁用缓存以测试负载均衡
            )
            
            provider = response.provider.value
            provider_usage[provider] = provider_usage.get(provider, 0) + 1
            
            print(f"   请求 {i}: {provider}")
            
        except Exception as e:
            print(f"   请求 {i}: 错误 - {str(e)}")
    
    print("\n📊 负载分布:")
    for provider, count in provider_usage.items():
        print(f"   {provider}: {count}次 ({count/10*100:.1f}%)")


async def custom_cache_example():
    """自定义缓存示例"""
    print("\n" + "=" * 60)
    print("自定义缓存示例")
    print("=" * 60)
    
    load_dotenv()
    
    # 创建自定义缓存管理器
    cache_backend = MemoryCacheBackend(max_size=100)
    cache_manager = CacheManager(
        backend=cache_backend,
        default_ttl=60,  # 60秒过期
        enabled=True
    )
    
    gateway = AIGateway(cache_manager=cache_manager)
    
    if os.getenv("GITHUB_TOKEN"):
        gateway.add_provider(
            "github",
            GitHubModelsProvider(api_key=os.getenv("GITHUB_TOKEN"))
        )
    
    messages = [
        Message(role=MessageRole.USER, content="What is 1+1?")
    ]
    
    print("\n📤 第1次请求...")
    response1 = await gateway.complete(
        messages=messages,
        model="gpt-4o-mini"
    )
    print(f"   Cached: {response1.cached}")
    print(f"   Latency: {response1.latency_ms:.2f}ms")
    
    print("\n📤 第2次请求（应该从缓存返回）...")
    response2 = await gateway.complete(
        messages=messages,
        model="gpt-4o-mini"
    )
    print(f"   Cached: {response2.cached}")
    print(f"   Latency: {response2.latency_ms:.2f}ms")
    
    # 查看缓存统计
    cache_stats = await cache_manager.get_stats()
    print("\n📊 缓存统计:")
    print(f"   大小: {cache_stats['size']}/{cache_stats['max_size']}")
    print(f"   命中率: {cache_stats['hit_rate']:.2%}")
    print(f"   命中次数: {cache_stats['hits']}")
    print(f"   未命中次数: {cache_stats['misses']}")


async def health_check_example():
    """健康检查示例"""
    print("\n" + "=" * 60)
    print("健康检查示例")
    print("=" * 60)
    
    load_dotenv()
    
    gateway = AIGateway()
    
    # 添加提供商
    if os.getenv("GITHUB_TOKEN"):
        gateway.add_provider(
            "github",
            GitHubModelsProvider(api_key=os.getenv("GITHUB_TOKEN"))
        )
    
    if os.getenv("OPENAI_API_KEY"):
        gateway.add_provider(
            "openai",
            OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
        )
    
    # 执行健康检查
    print("\n🏥 执行健康检查...")
    health = await gateway.health_check()
    
    print("\n📊 健康状态:")
    for provider, is_healthy in health.items():
        status = "✅ 健康" if is_healthy else "❌ 不健康"
        print(f"   {provider}: {status}")


async def error_handling_example():
    """错误处理示例"""
    print("\n" + "=" * 60)
    print("错误处理示例")
    print("=" * 60)
    
    gateway = AIGateway(enable_retry=True, max_retries=3)
    
    # 使用无效的API密钥
    gateway.add_provider(
        "invalid",
        GitHubModelsProvider(api_key="invalid_key")
    )
    
    messages = [
        Message(role=MessageRole.USER, content="Hello")
    ]
    
    print("\n📤 尝试使用无效的API密钥...")
    
    try:
        response = await gateway.complete(
            messages=messages,
            model="gpt-4o-mini"
        )
    except Exception as e:
        print(f"✅ 成功捕获错误: {type(e).__name__}")
        print(f"   错误信息: {str(e)[:100]}...")


async def provider_management_example():
    """提供商管理示例"""
    print("\n" + "=" * 60)
    print("提供商管理示例")
    print("=" * 60)
    
    load_dotenv()
    
    gateway = AIGateway()
    
    if os.getenv("GITHUB_TOKEN"):
        gateway.add_provider(
            "github",
            GitHubModelsProvider(api_key=os.getenv("GITHUB_TOKEN"))
        )
        print("✅ 添加提供商: github")
    
    # 查看统计
    stats = await gateway.get_stats()
    print(f"\n当前提供商: {list(stats['providers'].keys())}")
    
    # 禁用提供商
    print("\n⏸️  禁用提供商: github")
    gateway.disable_provider("github")
    
    stats = await gateway.get_stats()
    print(f"   github 已启用: {stats['providers']['github']['enabled']}")
    
    # 重新启用
    print("\n▶️  重新启用提供商: github")
    gateway.enable_provider("github")
    
    stats = await gateway.get_stats()
    print(f"   github 已启用: {stats['providers']['github']['enabled']}")


async def batch_requests_example():
    """批量请求示例"""
    print("\n" + "=" * 60)
    print("批量请求示例")
    print("=" * 60)
    
    load_dotenv()
    
    gateway = AIGateway()
    
    if os.getenv("GITHUB_TOKEN"):
        gateway.add_provider(
            "github",
            GitHubModelsProvider(api_key=os.getenv("GITHUB_TOKEN"))
        )
    
    # 准备多个请求
    questions = [
        "What is AI?",
        "What is ML?",
        "What is DL?",
        "What is NLP?",
        "What is CV?"
    ]
    
    print(f"\n📤 并发发送 {len(questions)} 个请求...")
    
    # 并发执行
    import time
    start = time.time()
    
    tasks = [
        gateway.complete(
            messages=[Message(role=MessageRole.USER, content=q)],
            model="gpt-4o-mini"
        )
        for q in questions
    ]
    
    responses = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    
    print(f"\n✅ 完成! 总耗时: {elapsed:.2f}秒")
    print(f"   平均每个请求: {elapsed/len(questions):.2f}秒")
    
    for i, (q, r) in enumerate(zip(questions, responses), 1):
        print(f"\n{i}. {q}")
        print(f"   {r.content[:80]}...")


async def main():
    """主函数"""
    examples = [
        ("负载均衡", load_balancing_example),
        ("自定义缓存", custom_cache_example),
        ("健康检查", health_check_example),
        ("错误处理", error_handling_example),
        ("提供商管理", provider_management_example),
        ("批量请求", batch_requests_example),
    ]
    
    print("\n🚀 AI Gateway 高级功能示例\n")
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{'='*60}")
        print(f"示例 {i}/{len(examples)}: {name}")
        print('='*60)
        
        try:
            await func()
        except Exception as e:
            print(f"\n❌ 示例执行失败: {str(e)}")
        
        if i < len(examples):
            await asyncio.sleep(1)  # 短暂暂停


if __name__ == "__main__":
    asyncio.run(main())
