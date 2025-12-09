@echo off
title Claude Profile Manager - Build and Run

echo ============================================
echo  Claude Profile Manager v2.0
echo  Build and Run Script
echo ============================================
echo.

echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python não está instalado ou não está no PATH
    echo    Por favor instale Python 3.8+ e tente novamente
    pause
    exit /b 1
)
python --version

echo.
echo ⚡ Executando aplicação...
echo.

REM Run the application directly
python main.py

REM Check if user wants to build executable
if errorlevel 1 (
    echo.
    echo ❌ Erro ao executar aplicação
    echo.
    set /p build_choice=Deseja tentar fazer build do executável? (s/N):
    if /i "%build_choice%"=="s" goto build
    goto end
)

echo.
set /p build_choice=Aplicação executou com sucesso! Deseja criar executável (.exe)? (s/N):
if /i not "%build_choice%"=="s" goto end

:build
echo.
echo 🔨 Iniciando build do executável...
echo.

REM Run build script
python build.py

if errorlevel 1 (
    echo ❌ Build falhou
    goto end
)

echo.
echo ✅ Build concluído com sucesso!
echo.
echo 📁 Executável disponível em: release\ClaudeProfileManager.exe
echo.

set /p run_exe=Deseja executar o .exe agora? (s/N):
if /i "%run_exe%"=="s" (
    if exist "release\ClaudeProfileManager.exe" (
        echo 🚀 Executando...
        start "" "release\ClaudeProfileManager.exe"
    ) else (
        echo ❌ Executável não encontrado
    )
)

:end
echo.
echo 👋 Pressione qualquer tecla para sair...
pause >nul