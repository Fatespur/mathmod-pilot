@echo off
chcp 65001 >nul
title CUMCM Modeling Skills 可视化官网

echo ================================================================
echo   CUMCM Modeling Skills - 可视化技能官网启动器
echo ================================================================
echo.
echo 正在为您在默认浏览器中打开可视化官网...
echo.

start "" "%~dp0index.html"

echo [提示] 官网已在默认浏览器中成功打开！
echo.
echo 若需要本地 HTTP 服务方式，可在终端执行：
echo    python -m http.server 8080
echo 并访问：http://127.0.0.1:8080
echo ================================================================
echo 按任意键退出...
pause >nul
