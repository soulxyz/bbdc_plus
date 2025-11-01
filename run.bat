@echo off
chcp 65001 >nul
echo ===============================================================================
echo   BBDC Plus - 背单词增强工具
echo ===============================================================================
echo.
echo 启动中...
echo.

REM 检查是否以管理员权限运行
net session >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告：未以管理员权限运行！
    echo    全局快捷键可能无法使用
    echo.
    echo    建议：右键点击此文件 → 以管理员身份运行
    echo.
    timeout /t 3 >nul
)

python main.py

if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错
    pause
)

