#!/usr/bin/env python3
"""
命令行演示脚本
在终端中快速测试 Agent 功能
"""

import asyncio
import sys
import os
from agents.travel_agent import TravelAgent


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print("=" * 60)


def print_user(text):
    """打印用户消息"""
    print(f"\n{Colors.CYAN}👤 用户: {text}{Colors.ENDC}")


def print_agent(text):
    """打印 Agent 响应"""
    print(f"\n{Colors.GREEN}🤖 助手: {text}{Colors.ENDC}")


def print_error(text):
    """打印错误"""
    print(f"\n{Colors.FAIL}❌ 错误: {text}{Colors.ENDC}")


def print_info(text):
    """打印信息"""
    print(f"{Colors.WARNING}ℹ️  {text}{Colors.ENDC}")


async def run_demo():
    """运行演示"""
    print_header("🌍 智能旅游助手 - 命令行演示")
    
    print_info("正在初始化 Agent...")
    
    try:
        agent = TravelAgent()
        print_info("✅ Agent 初始化成功!\n")
    except Exception as e:
        print_error(f"初始化失败: {str(e)}")
        print_info("\n请检查:")
        print_info("1. .env 文件是否存在")
        print_info("2. GITHUB_TOKEN 是否正确配置")
        return
    
    # 预设的演示对话
    demo_conversations = [
        "有哪些目的地可以选择?",
        "巴黎现在可以预订吗?",
        "推荐一个预算中等、喜欢美食的地方",
    ]
    
    print_header("📝 自动演示模式")
    print_info("将自动运行预设对话...\n")
    
    for i, question in enumerate(demo_conversations, 1):
        print(f"\n{Colors.BOLD}--- 对话 {i}/{len(demo_conversations)} ---{Colors.ENDC}")
        print_user(question)
        
        try:
            response = await agent.chat(question)
            print_agent(response)
        except Exception as e:
            print_error(f"处理失败: {str(e)}")
        
        # 短暂暂停,让用户有时间阅读
        await asyncio.sleep(2)
    
    # 交互模式
    print_header("💬 交互模式")
    print_info("现在你可以自由提问了!")
    print_info("输入 'quit' 或 'exit' 退出\n")
    
    while True:
        try:
            user_input = input(f"{Colors.CYAN}👤 你: {Colors.ENDC}").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print_info("\n👋 再见!祝你旅途愉快!")
                break
            
            if user_input.lower() == 'reset':
                await agent.reset()
                print_info("✅ 对话已重置")
                continue
            
            response = await agent.chat(user_input)
            print_agent(response)
            
        except KeyboardInterrupt:
            print_info("\n\n👋 再见!")
            break
        except Exception as e:
            print_error(f"处理失败: {str(e)}")


async def run_quick_test():
    """快速测试模式"""
    print_header("⚡ 快速测试模式")
    
    print_info("测试 1: 初始化 Agent")
    try:
        agent = TravelAgent()
        print(f"{Colors.GREEN}✅ 通过{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ 失败: {str(e)}{Colors.ENDC}")
        return
    
    print_info("\n测试 2: 查询目的地")
    try:
        response = await agent.chat("有哪些目的地?")
        assert len(response) > 0
        print(f"{Colors.GREEN}✅ 通过{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ 失败: {str(e)}{Colors.ENDC}")
        return
    
    print_info("\n测试 3: 查询可用性")
    try:
        response = await agent.chat("巴黎可以预订吗?")
        assert len(response) > 0
        print(f"{Colors.GREEN}✅ 通过{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ 失败: {str(e)}{Colors.ENDC}")
        return
    
    print_info("\n测试 4: 获取推荐")
    try:
        response = await agent.chat("推荐一个预算中等的地方")
        assert len(response) > 0
        print(f"{Colors.GREEN}✅ 通过{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ 失败: {str(e)}{Colors.ENDC}")
        return
    
    print_header("🎉 所有测试通过!")


def print_menu():
    """打印菜单"""
    print_header("🌍 智能旅游助手 - 演示程序")
    print("\n选择运行模式:")
    print(f"  {Colors.BLUE}1.{Colors.ENDC} 完整演示 (自动 + 交互)")
    print(f"  {Colors.BLUE}2.{Colors.ENDC} 快速测试")
    print(f"  {Colors.BLUE}3.{Colors.ENDC} 仅交互模式")
    print(f"  {Colors.BLUE}q.{Colors.ENDC} 退出\n")


async def interactive_mode():
    """仅交互模式"""
    print_header("💬 交互模式")
    
    print_info("正在初始化...")
    try:
        agent = TravelAgent()
        print_info("✅ 准备就绪!\n")
    except Exception as e:
        print_error(f"初始化失败: {str(e)}")
        return
    
    print_info("输入你的问题,或输入 'quit' 退出\n")
    
    while True:
        try:
            user_input = input(f"{Colors.CYAN}👤 你: {Colors.ENDC}").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print_info("\n👋 再见!")
                break
            
            if user_input.lower() == 'reset':
                await agent.reset()
                print_info("✅ 对话已重置")
                continue
            
            response = await agent.chat(user_input)
            print_agent(response)
            
        except KeyboardInterrupt:
            print_info("\n\n👋 再见!")
            break
        except Exception as e:
            print_error(f"处理失败: {str(e)}")


async def main():
    """主函数"""
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "test":
            await run_quick_test()
        elif mode == "demo":
            await run_demo()
        elif mode == "chat":
            await interactive_mode()
        else:
            print_error(f"未知模式: {mode}")
            print_info("可用模式: test, demo, chat")
        return
    
    while True:
        print_menu()
        choice = input(f"{Colors.CYAN}请选择 (1-3, q): {Colors.ENDC}").strip()
        
        if choice == '1':
            await run_demo()
        elif choice == '2':
            await run_quick_test()
        elif choice == '3':
            await interactive_mode()
        elif choice.lower() in ['q', 'quit', 'exit']:
            print_info("\n👋 再见!")
            break
        else:
            print_error("无效选择,请输入 1-3 或 q")
        
        input(f"\n{Colors.WARNING}按 Enter 继续...{Colors.ENDC}")


if __name__ == "__main__":
    print(f"\n{Colors.BOLD}智能旅游助手 v1.0{Colors.ENDC}")
    print(f"{Colors.WARNING}提示: 可以直接运行 'python demo.py [test|demo|chat]'{Colors.ENDC}\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_info("\n\n👋 程序已退出")
