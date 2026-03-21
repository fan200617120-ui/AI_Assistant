@echo off
chcp 65001 >nul
title 轻舟 AI・LightShip AI 启动器
color 0B

:menu
cls
echo ========================================
echo           轻舟 AI・LightShip AI
echo ========================================
echo.
echo          轻舟渡万境，一智载千灵。
echo.
echo 请选择要启动的选项（直接输入数字）：
echo.
echo    [1] 启动 Ollama 服务 + 有记忆版聊天界面
echo.
echo    [2] 启动 Ollama 服务 + 无记忆版聊天界面
echo.
echo    [3] 仅启动 Ollama 服务（不打开界面）
echo.
echo    [4] 退出
echo.
set /p choice="请输入数字 (1-4): "

:: 去除用户输入中的无效字符
set "choice=%choice:[=%"
set "choice=%choice:]=%"
set "choice=%choice: =%"

if "%choice%"=="1" goto start_memory
if "%choice%"=="2" goto start_nomemory
if "%choice%"=="3" goto start_service_only
if "%choice%"=="4" goto exit

echo.
echo 无效输入，请输入 1、2、3 或 4。
pause
goto menu

:start_memory
set SCRIPT=chat_Ai.py
goto start_both

:start_nomemory
set SCRIPT=chat_Ai_no.py
goto start_both

:start_both
echo.
echo ========================================
echo 正在启动 Ollama 服务...
echo ========================================
if not exist "%~dp0models" mkdir "%~dp0models"
start "Ollama服务" cmd /c "set OLLAMA_MODELS=%~dp0models && ollama serve"

:: 等待服务启动（可根据实际情况调整）
echo.
echo 等待服务初始化（约3秒）...
echo.
timeout /t 3 /nobreak >nul
echo.
echo ========================================
echo 正在启动 AI助手界面（%SCRIPT%）...
echo ========================================
if not exist "%~dp0python_embeded\python.exe" (
    echo 错误：未找到 python_embeded\python.exe
    echo 请确认已将 Python 嵌入包解压到当前目录的 python_embeded 文件夹。
    pause
    goto menu
)

"%~dp0python_embeded\python.exe" "%~dp0core\%SCRIPT%"

echo.
echo 界面已关闭，按任意键返回主菜单...
pause
goto menu

:start_service_only
echo.
echo ========================================
echo 正在启动 Ollama 服务（仅服务）...
echo ========================================
echo.
if not exist "%~dp0models" mkdir "%~dp0models"
start "Ollama服务" cmd /c "set OLLAMA_MODELS=%~dp0models && ollama serve"
echo.
echo Ollama 服务已在新窗口启动。
echo.
echo 请勿关闭该窗口。
echo.
echo 提示：如需永久指定模型目录，可设置系统环境变量 OLLAMA_MODELS=%~dp0models
pause
goto menu

:exit
echo 正在退出...
timeout /t 1 >nul
exit
