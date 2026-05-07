#!/bin/bash

# 会议室预约系统部署脚本

set -e

echo "==================================="
echo "  会议室预约系统部署脚本"
echo "==================================="

# 检查是否在项目根目录
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "错误: 请在项目根目录下运行此脚本"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "错误: 未找到 Python"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 Node.js"
    exit 1
fi

echo ""
echo "请选择部署类型:"
echo "  1. 开发模式 (前后端分别启动)"
echo "  2. 生产模式 (构建前端静态文件 + 启动后端)"
read -p "请输入选择 (1/2): " deploy_type

case $deploy_type in
    1)
        echo ""
        echo ">>> 开发模式部署"

        echo "安装后端依赖..."
        cd backend
        pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt
        cd ..

        echo "启动后端服务 (端口 8000)..."
        cd backend
        python3 main.py &
        BACKEND_PID=$!
        cd ..

        echo "启动前端服务 (端口 3000)..."
        cd frontend
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        npm run dev &
        FRONTEND_PID=$!
        cd ..

        echo ""
        echo ">>> 开发模式启动完成!"
        echo "   后端：http://localhost:8000"
        echo "   API文档：http://localhost:8000/docs"
        echo "   前端：http://localhost:3000"
        echo ""
        echo "按 Ctrl+C 停止服务..."
        wait $BACKEND_PID $FRONTEND_PID
        ;;

    2)
        echo ""
        echo ">>> 生产模式部署"

        echo "安装后端依赖..."
        cd backend
        pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt
        cd ..

        echo "构建前端静态文件..."
        cd frontend
        npm install
        npm run build
        cd ..

        echo ""
        echo ">>> 前端构建完成"
        echo "启动后端服务..."
        cd backend
        echo "运行: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4"
        uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
        ;;

    *)
        echo "无效选择"
        exit 1
        ;;
esac
