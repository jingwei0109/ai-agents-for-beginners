#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║     🌍 智能旅游助手 - 一键启动脚本               ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  未找到 .env 文件${NC}"
    echo ""
    echo "正在创建 .env 文件..."
    cp .env.example .env
    echo ""
    echo -e "${GREEN}✅ .env 文件已创建!${NC}"
    echo ""
    echo -e "${YELLOW}📝 重要提示:${NC}"
    echo "   1. 请在 Cursor 中打开 .env 文件"
    echo "   2. 填入你的 GITHUB_TOKEN"
    echo "   3. 获取 Token: https://github.com/settings/tokens"
    echo ""
    read -p "按 Enter 继续编辑 .env 文件..." 
    
    # 尝试用默认编辑器打开
    ${EDITOR:-nano} .env
fi

# 检查是否配置了 Token
if ! grep -q "^GITHUB_TOKEN=ghp_" .env 2>/dev/null; then
    echo -e "${RED}❌ GITHUB_TOKEN 未配置或格式不正确${NC}"
    echo ""
    echo "请在 .env 文件中正确配置 GITHUB_TOKEN"
    echo "格式: GITHUB_TOKEN=ghp_your_token_here"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ 配置检查通过!${NC}"
echo ""

# 检查依赖
echo "正在检查依赖..."
if ! python3 -c "import semantic_kernel" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  依赖未安装${NC}"
    echo ""
    read -p "是否安装依赖? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在安装依赖..."
        pip install -r requirements.txt
        echo ""
        echo -e "${GREEN}✅ 依赖安装完成!${NC}"
    else
        echo -e "${RED}❌ 无法继续,请先安装依赖${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ 依赖已安装${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "请选择运行模式:"
echo ""
echo -e "  ${BLUE}1.${NC} 🌐 Web 界面 (Chainlit) - 推荐"
echo -e "  ${BLUE}2.${NC} 🎮 命令行演示 (完整)"
echo -e "  ${BLUE}3.${NC} ⚡ 快速测试"
echo -e "  ${BLUE}4.${NC} 💬 仅交互模式"
echo -e "  ${BLUE}5.${NC} 📖 查看文档"
echo -e "  ${BLUE}q.${NC} 退出"
echo ""

read -p "请选择 (1-5, q): " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}🚀 启动 Web 界面...${NC}"
        echo ""
        echo "浏览器将自动打开 http://localhost:8000"
        echo "按 Ctrl+C 停止服务器"
        echo ""
        chainlit run app.py -w
        ;;
    2)
        echo ""
        echo -e "${GREEN}🎮 启动命令行演示...${NC}"
        echo ""
        python demo.py
        ;;
    3)
        echo ""
        echo -e "${GREEN}⚡ 运行快速测试...${NC}"
        echo ""
        python demo.py test
        ;;
    4)
        echo ""
        echo -e "${GREEN}💬 进入交互模式...${NC}"
        echo ""
        python demo.py chat
        ;;
    5)
        echo ""
        echo -e "${GREEN}📖 文档导航:${NC}"
        echo ""
        echo "• README.md - 项目说明"
        echo "• 快速启动指南.md - 5分钟入门"
        echo "• 快速参考卡.md - 命令速查"
        echo "• ARCHITECTURE.md - 架构设计"
        echo ""
        echo "在 Cursor 中打开这些文件进行阅读"
        echo ""
        ;;
    q|Q)
        echo ""
        echo -e "${YELLOW}👋 再见!${NC}"
        echo ""
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}❌ 无效选择${NC}"
        echo ""
        exit 1
        ;;
esac
