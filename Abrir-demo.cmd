@echo off
setlocal
cd /d "%~dp0"
set "DEMO_PYTHON="
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys" >nul 2>nul
    if not errorlevel 1 set "DEMO_PYTHON=py"
)
set "CODEX_PYTHON=%ProgramFiles%\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1118-904-0_26.1118.904.0_x64__3k8sg7r9htsxt\dependencies\python\python.exe"
if not defined DEMO_PYTHON if exist "%CODEX_PYTHON%" set "DEMO_PYTHON=%CODEX_PYTHON%"
if not defined DEMO_PYTHON (
    for /d %%P in ("%ProgramFiles%\WindowsApps\OpenAI.CodexPrimaryRuntime.*") do (
        if exist "%%~fP\dependencies\python\python.exe" set "DEMO_PYTHON=%%~fP\dependencies\python\python.exe"
    )
)
if not defined DEMO_PYTHON (
    echo Se necesita Python 3 para iniciar la demo.
    pause
    exit /b 1
)
echo Abre http://127.0.0.1:8769 en tu navegador.
if "%DEMO_PYTHON%"=="py" (
    py -3 -X utf8 -B -m agents_d4.app --port 8769
) else (
    "%DEMO_PYTHON%" -X utf8 -B -m agents_d4.app --port 8769
)
pause
