@echo off
chcp 65001 >nul
echo ============================================================
echo 算网大脑调度系统 - 快速启动脚本
echo ============================================================
echo.

echo [1/4] 检查 Docker 环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Docker，请先安装 Docker Desktop
    pause
    exit /b 1
)
echo [OK] Docker 已安装

echo.
echo [2/4] 构建 Docker 镜像...
docker-compose build

echo.
echo [3/4] 启动所有服务...
docker-compose up -d

echo.
echo [4/4] 等待服务启动...
timeout /t 5 /nobreak >nul

echo.
echo ============================================================
echo 服务启动完成！
echo ============================================================
echo.
echo 访问地址:
echo   - 系统首页：http://localhost
echo   - 编排服务 API 文档：http://localhost:8080/docs
echo.
echo 架构说明:
echo   - 编排服务(8080): 大管家，内嵌光网+算力南向适配
echo   - API网关(80): 统一入口，只代理编排服务
echo.
echo 查看日志：docker-compose logs -f
echo 停止服务：docker-compose down
echo.
echo ============================================================
pause
