@echo off
chcp 65001 >nul
title 轻舟 AI・LightShip AI 启动器 (llama.cpp)
color 0B

:: 获取当前脚本所在目录（绝对路径）
set "BASE_DIR=%~dp0"
set "PYTHON=%BASE_DIR%python_embeded\python.exe"
set "CORE_DIR=%BASE_DIR%core"
set "MODELS_DIR=%BASE_DIR%models"
set "LLAMA_DIR=%BASE_DIR%llama"
set "LLAMA_SERVER=%LLAMA_DIR%\llama-server.exe"

:: 确保 models 目录存在
if not exist "%MODELS_DIR%" mkdir "%MODELS_DIR%"

:: 检查 llama-server.exe 是否存在
if not exist "%LLAMA_SERVER%" (
    echo 错误：未找到 %LLAMA_SERVER%
    echo 请确认 llama.cpp 已放置在 %LLAMA_DIR% 目录下
    pause
    exit /b 1
)

:menu
cls
echo ========================================
echo        轻舟 AI・LightShip AI
echo ========================================
echo.
echo              llama.cpp 
echo.
echo ========================================
echo       轻舟渡万境，一智载千寻!
echo ========================================
echo.
echo 模型存储路径：%MODELS_DIR%
echo.
echo 请选择要运行的选项（输入数字或字母）：
echo.
echo   [1] 原生浏览器窗口
echo.
echo   [2] AI助手 (ai_buddy.py)
echo.
echo   [3] 字幕翻译 (subtitle_translator.py)
echo.
echo   [4] 有记忆版聊天 (chat_Ai.py)
echo.
echo   [5] 无记忆版聊天 (chat_Ai_no.py)
echo.
echo   [6] 打开资源管理器到根目录
echo.
echo   [7] 退出
echo.
set /p choice="请输入数字 (1-7): "

:: 去除无效字符
set "choice=%choice:[=%"
set "choice=%choice:]=%"
set "choice=%choice: =%"

if "%choice%"=="1" goto start_service_and_browser
if "%choice%"=="2" set SCRIPT=ai_buddy.py & goto run_with_service
if "%choice%"=="3" set SCRIPT=subtitle_translator.py & goto run_with_service
if "%choice%"=="4" set SCRIPT=chat_Ai.py & goto run_with_service
if "%choice%"=="5" set SCRIPT=chat_Ai_no.py & goto run_with_service
if "%choice%"=="6" goto explorer
if "%choice%"=="7" goto exit

echo 无效输入，请输入 1-7。
pause
goto menu

:run_with_service
:: 先启动 llama-server 服务，再运行脚本
echo.
echo ========================================
echo 正在关闭可能运行的 llama-server 进程...
echo ========================================
echo.
taskkill /f /im llama-server.exe 2>nul
timeout /t 2 /nobreak >nul

echo 正在启动 llama-server（模型目录：%MODELS_DIR%）...
echo.
echo 服务地址：http://127.0.0.1:8080
echo.
start "llama-server" cmd /c "%LLAMA_SERVER% --models-dir "%MODELS_DIR%""
:: 等待服务完全启动（根据机器性能可适当调整）
echo.
echo 等待服务启动...
timeout /t 5 /nobreak >nul

goto run_script

:run_script
if not exist "%PYTHON%" (
    echo 错误：未找到 %PYTHON%
    pause
    goto menu
)
"%PYTHON%" "%CORE_DIR%\%SCRIPT%"
pause
goto menu

:start_service_and_browser
echo.
echo ========================================
echo 正在关闭可能运行的 llama-server 进程...
echo ========================================
echo.
taskkill /f /im llama-server.exe 2>nul
timeout /t 2 /nobreak >nul

echo 正在启动 llama-server（模型目录：%MODELS_DIR%）...
echo 服务地址：http://127.0.0.1:8080
start "llama-server" cmd /c "%LLAMA_SERVER% --models-dir "%MODELS_DIR%""
:: 等待服务启动
echo 等待服务启动...
timeout /t 5 /nobreak >nul

:: 打开默认浏览器访问 Web UI
echo 正在打开浏览器...
start http://127.0.0.1:8080

echo llama-server 服务已启动，浏览器已打开。
echo.
echo 提示：按任意键返回菜单...
pause
goto menu

:explorer
start "" "%BASE_DIR%"
pause
goto menu

:exit
exit