#!/bin/bash

# 会议室预约系统上传到 Gitee 脚本

echo "==================================="
echo "  会议室预约系统上传到 Gitee"
echo "==================================="

# 检查 Git 是否安装
if ! command -v git &> /dev/null; then
    echo "错误: Git 未安装"
    echo "  Ubuntu/Debian: sudo apt install git -y"
    echo "  CentOS/RHEL: sudo yum install git -y"
    exit 1
fi
echo "[OK] Git 已安装"

# 确认在项目根目录
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "错误: 请在项目根目录下运行此脚本"
    exit 1
fi

# 检查是否已初始化 Git
if [ ! -d ".git" ]; then
    echo "初始化 Git 仓库..."
    git init
else
    echo "[OK] Git 仓库已存在"
fi

# 检查 .gitignore 是否存在
if [ ! -f ".gitignore" ]; then
    echo "创建 .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
build/
dist/
*.egg-info/
venv/
env/

# Frontend
node_modules/
dist/

# Database
*.db
*.db-journal

# Logs
logs/
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.*
EOF
    echo "[OK] .gitignore 已创建"
fi

# 添加文件
echo "添加文件到 Git..."
git add .

# 检查是否需要提交
if git diff --cached --quiet 2>/dev/null; then
    echo "没有需要提交的更改"
else
    echo "输入提交信息 (直接回车使用默认信息):"
    read -p "> " commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="Update: 会议室预约系统"
    fi
    git commit -m "$commit_msg"
    echo "[OK] 已提交"
fi

echo ""
echo "==================================="
echo "  下一步:"
echo "  1. 在 Gitee 创建新仓库"
echo "  2. 执行以下命令推送:"
echo ""
echo "     git remote add origin <仓库地址>"
echo "     git branch -M main"
echo "     git push -u origin main"
echo "==================================="
