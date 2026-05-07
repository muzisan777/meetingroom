@echo off
chcp 65001 >nul
echo ========================================
echo   会议室预约系统 - 快速启动
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查 Node.js
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)

echo 安装后端依赖...
cd backend
pip install -r requirements.txt >nul 2>&1
cd ..

echo 安装前端依赖...
cd frontend
if not exist "node_modules" (
    call npm install
) else (
    echo 已存在，跳过
)
cd ..

echo.
echo [1/3] 启动后端服务...
start "MeetingRoom-Backend" cmd /k "cd /d %~dp0backend && python main.py"
timeout /t 5 /nobreak >nul

echo [2/3] 启动前端服务...
start "MeetingRoom-Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo   后端：http://localhost:8000
echo   API文档：http://localhost:8000/docs
echo   前端：http://localhost:3000
echo.
echo   测试账号:
echo     管理员：admin / admin@123
echo     普通用户：user1 / user123
echo.
echo   按任意键退出此窗口...
pause >nul
