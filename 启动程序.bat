@echo off
chcp 65001 >nul
title AI模型切换器

echo.
echo ========================================
echo   AI模型切换器 v1.0
echo   智谱AI + DeepSeek 模型切换工具
echo ========================================
echo.

python model_switcher.py

if errorlevel 1 (
    echo.
    echo [错误] 程序启动失败
    echo.
    echo 请确保已安装Python和requests库：
    echo   pip install requests
    echo.
    pause
)
