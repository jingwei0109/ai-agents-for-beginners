#!/usr/bin/env python3
"""
AI Gateway 演示程序
展示核心功能的交互式演示
"""

import asyncio
import os
from dotenv import load_dotenv

from ai_gateway import (
    AIGateway,
    OpenAIProvider,
    GitHubModelsProvider,
    AzureOpenAIProvider,
    Message,
    MessageRole,
    CacheManager
)


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_section(text):
    """打印章节"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.ENDC}\n")


def print_info(text):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")


def print_success(text):
    """打印成功消息"""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    """打印错误消息"""
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")


def print_warning(text):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")


async def setup_gateway():
    """设置网关"""
    print_section("🔧 初始化 AI Gateway")
    
    load_dotenv()
    
    gateway = AIGateway(
        enable_cache=True,
        enable_retry=True,
        max_retries=3
    )
    
    print_info("创建网关实例...")
    print_success("网关创建成功\n")
    
    # 添加提供商
    providers_added = 0
    
    if os.getenv("GITHUB_TOKEN"):
        gateway.add_provider(
            name="github",
            provider=GitHubModelsProvider(api_key=os.getenv("GITHUB_TOKEN")),
            priority=1,
            weight=1
        )
        print_success("已添加: GitHub Models (优先级: 1, 权重: 1)")
        providers_added += 1
    
    if os.getenv("OPENAI_API_KEY"):
        gateway.add_provider(
            name="openai",
            provider=OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY")),
            priority=2,
            weight=1
        )
        print_success("已添加: OpenAI (优先级: 2, 权重: 1)")
        providers_added += 1
    
    if os.getenv("AZURE_OPENAI_API_KEY"):
        gateway.add_provider(
            name="azure",
            provider=AzureOpenAIProvider(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")
            ),
            priority=2,
            weight=1
        )
        print_success("已添加: Azure OpenAI (优先级: 2, 权重: 1)")
        providers_added += 1
    
    if providers_added == 0:
        print_error("未找到有效的API密钥")
        print_info("请在 .env 文件中配置至少一个提供商的API密钥")
        return None
    
    print(f"\n{Colors.BOLD}总计: {providers_added} 个提供商已就绪{Colors.ENDC}")
    
    return gateway


async def demo_basic_request(gateway):
    """演示基础请求"""
    print_section("📤 演示 1: 基础请求")
    
    messages = [
        Message(
            role=MessageRole.SYSTEM,
            content="你是一个helpful assistant"
        ),
        Message(
            role=MessageRole.USER,
            content="用一句话解释什么是AI Gateway"
        )
    ]
    
    print_info("发送请求...")
    print(f"   问题: {messages[1].content}")
    
    try:
        response = await gateway.complete(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.7
        )
        
        print_success("收到响应\n")
        print(f"{Colors.BOLD}响应详情:{Colors.ENDC}")
        print(f"  • Provider: {Colors.CYAN}{response.provider.value}{Colors.ENDC}")
        print(f"  • Model: {Colors.CYAN}{response.model}{Colors.ENDC}")
        print(f"  • Latency: {Colors.CYAN}{response.latency_ms:.2f}ms{Colors.ENDC}")
        print(f"  • Cached: {Colors.CYAN}{response.cached}{Colors.ENDC}")
        print(f"  • Tokens: {Colors.CYAN}{response.usage['total_tokens']}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}回答:{Colors.ENDC}")
        print(f"  {Colors.GREEN}{response.content}{Colors.ENDC}")
        
        return True
        
    except Exception as e:
        print_error(f"请求失败: {str(e)}")
        return False


async def demo_cache(gateway):
    """演示缓存功能"""
    print_section("💾 演示 2: 智能缓存")
    
    messages = [
        Message(role=MessageRole.USER, content="What is 1+1?")
    ]
    
    # 第一次请求
    print_info("第1次请求（无缓存）...")
    response1 = await gateway.complete(
        messages=messages,
        model="gpt-4o-mini"
    )
    
    print(f"  • Cached: {Colors.RED}False{Colors.ENDC}")
    print(f"  • Latency: {Colors.YELLOW}{response1.latency_ms:.2f}ms{Colors.ENDC}")
    
    # 第二次请求（相同内容）
    print_info("\n第2次请求（相同内容，应该命中缓存）...")
    response2 = await gateway.complete(
        messages=messages,
        model="gpt-4o-mini"
    )
    
    print(f"  • Cached: {Colors.GREEN}True{Colors.ENDC}")
    print(f"  • Latency: {Colors.GREEN}{response2.latency_ms:.2f}ms{Colors.ENDC}")
    
    # 计算性能提升
    speedup = response1.latency_ms / response2.latency_ms
    print(f"\n{Colors.BOLD}性能提升: {Colors.GREEN}{speedup:.1f}x{Colors.ENDC}")


async def demo_stream(gateway):
    """演示流式输出"""
    print_section("🌊 演示 3: 流式输出")
    
    messages = [
        Message(
            role=MessageRole.USER,
            content="写一首关于AI的五言绝句"
        )
    ]
    
    print_info("开始流式输出...\n")
    print(f"{Colors.BOLD}回答:{Colors.ENDC}")
    
    try:
        async for chunk in gateway.complete_stream(
            messages=messages,
            model="gpt-4o-mini"
        ):
            print(f"{Colors.GREEN}{chunk}{Colors.ENDC}", end="", flush=True)
        
        print(f"\n\n{Colors.BOLD}✓ 流式输出完成{Colors.ENDC}")
        
    except Exception as e:
        print_error(f"\n流式输出失败: {str(e)}")


async def demo_stats(gateway):
    """演示统计信息"""
    print_section("📊 演示 4: 统计信息")
    
    stats = await gateway.get_stats()
    
    print(f"{Colors.BOLD}网关统计:{Colors.ENDC}")
    print(f"  • 总请求数: {Colors.CYAN}{stats['gateway']['total_requests']}{Colors.ENDC}")
    print(f"  • 缓存命中: {Colors.CYAN}{stats['gateway']['cache_hits']}{Colors.ENDC}")
    print(f"  • 缓存未命中: {Colors.CYAN}{stats['gateway']['cache_misses']}{Colors.ENDC}")
    
    if stats['cache']['total_requests'] > 0:
        print(f"  • 缓存命中率: {Colors.CYAN}{stats['cache']['hit_rate']:.2%}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}提供商使用情况:{Colors.ENDC}")
    for provider, count in stats['gateway']['provider_requests'].items():
        print(f"  • {provider}: {Colors.CYAN}{count}次{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}缓存信息:{Colors.ENDC}")
    print(f"  • 后端: {Colors.CYAN}{stats['cache']['backend']}{Colors.ENDC}")
    print(f"  • 大小: {Colors.CYAN}{stats['cache']['size']}/{stats['cache']['max_size']}{Colors.ENDC}")


async def demo_health_check(gateway):
    """演示健康检查"""
    print_section("🏥 演示 5: 健康检查")
    
    print_info("检查所有提供商的健康状态...\n")
    
    health = await gateway.health_check()
    
    print(f"{Colors.BOLD}健康状态:{Colors.ENDC}")
    for provider, is_healthy in health.items():
        status = f"{Colors.GREEN}✓ 健康{Colors.ENDC}" if is_healthy else f"{Colors.RED}✗ 不健康{Colors.ENDC}"
        print(f"  • {provider}: {status}")


async def interactive_mode(gateway):
    """交互模式"""
    print_section("💬 演示 6: 交互模式")
    
    print_info("进入交互模式，输入 'quit' 退出\n")
    
    while True:
        try:
            user_input = input(f"{Colors.CYAN}你: {Colors.ENDC}").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print_info("退出交互模式")
                break
            
            messages = [
                Message(role=MessageRole.USER, content=user_input)
            ]
            
            try:
                response = await gateway.complete(
                    messages=messages,
                    model="gpt-4o-mini"
                )
                
                print(f"{Colors.GREEN}AI: {response.content}{Colors.ENDC}\n")
                
            except Exception as e:
                print_error(f"错误: {str(e)}\n")
                
        except KeyboardInterrupt:
            print_info("\n退出交互模式")
            break


async def main():
    """主函数"""
    print_header("🚀 AI Gateway 演示程序")
    
    print(f"{Colors.BOLD}欢迎使用 AI Gateway!{Colors.ENDC}")
    print("这是一个通用的AI接口预取接入工具演示\n")
    
    # 设置网关
    gateway = await setup_gateway()
    
    if not gateway:
        return
    
    # 等待用户确认
    input(f"\n{Colors.YELLOW}按 Enter 开始演示...{Colors.ENDC}")
    
    # 运行演示
    demos = [
        ("基础请求", demo_basic_request),
        ("智能缓存", demo_cache),
        ("流式输出", demo_stream),
        ("统计信息", demo_stats),
        ("健康检查", demo_health_check),
    ]
    
    for i, (name, func) in enumerate(demos, 1):
        try:
            await func(gateway)
            
            if i < len(demos):
                input(f"\n{Colors.YELLOW}按 Enter 继续下一个演示...{Colors.ENDC}")
        
        except Exception as e:
            print_error(f"演示失败: {str(e)}")
            continue
    
    # 交互模式
    choice = input(f"\n{Colors.YELLOW}是否进入交互模式? (y/n): {Colors.ENDC}").strip().lower()
    if choice == 'y':
        await interactive_mode(gateway)
    
    # 结束
    print_header("🎉 演示完成")
    print(f"{Colors.BOLD}感谢使用 AI Gateway!{Colors.ENDC}\n")
    print("更多信息请查看:")
    print("  • README.md")
    print("  • examples/basic_usage.py")
    print("  • examples/advanced_usage.py")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}程序已退出{Colors.ENDC}")
