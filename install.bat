@echo off
chcp 65001 >nul
echo ===============================================================================
echo   BBDC Plus - 背单词增强工具
echo   安装脚本
echo ===============================================================================
echo.

echo [1/3] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 Python！
    echo    请先安装 Python 3.8 或更高版本
    echo    下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo ✅ Python 已安装
echo.

echo [2/3] 安装 Python 依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖包安装失败！
    pause
    exit /b 1
)
echo ✅ Python 依赖包安装完成
echo.

echo [3/3] 检查 Tesseract OCR...
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告：未找到 Tesseract OCR！
    echo.
    echo    Tesseract OCR 是必需的 OCR 识别引擎
    echo    请手动安装：
    echo    1. 下载：https://github.com/UB-Mannheim/tesseract/wiki
    echo    2. 安装时勾选 "Add to PATH"
    echo    3. 确保安装英文语言包
    echo.
    echo    如果已安装但未添加到 PATH，请在 config.py 中设置路径：
    echo    TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    echo.
) else (
    tesseract --version
    echo ✅ Tesseract OCR 已安装
    echo.
)

echo ===============================================================================
echo   安装完成！
echo ===============================================================================
echo.
echo 使用方法：
echo   1. 以管理员权限运行 run.bat
echo   2. 或直接运行：python main.py
echo.
echo 详细说明请查看 README.md
echo.
pause

