@echo off
REM Windows Batch Script for SRT-to-Audio Pipeline
REM This is a simple wrapper that calls the PowerShell script

setlocal enabledelayedexpansion

REM Check if PowerShell is available
where pwsh >nul 2>nul
if %errorlevel% neq 0 (
    where powershell >nul 2>nul
    if !errorlevel! neq 0 (
        echo Error: PowerShell not found. Please install PowerShell.
        echo You can download it from: https://github.com/PowerShell/PowerShell
        pause
        exit /b 1
    )
    set PS_CMD=powershell
) else (
    set PS_CMD=pwsh
)

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Check if input file is provided
if "%~1"=="" (
    echo Usage: %~nx0 ^<audio_file^> [whisper_model] [output_file]
    echo.
    echo Examples:
    echo   %~nx0 my_audio.mp3
    echo   %~nx0 my_audio.wav large
    echo   %~nx0 my_audio.mp3 medium my_output.mp3
    echo.
    pause
    exit /b 1
)

REM Build PowerShell command
set PS_SCRIPT=%SCRIPT_DIR%run_pipeline.ps1
set PS_ARGS=-InputAudioFile "%~1"

if not "%~2"=="" (
    set PS_ARGS=!PS_ARGS! -WhisperModel "%~2"
)

if not "%~3"=="" (
    set PS_ARGS=!PS_ARGS! -OutputAudio "%~3"
)

echo Running SRT-to-Audio Pipeline...
echo Command: %PS_CMD% -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %PS_ARGS%
echo.

REM Execute PowerShell script
%PS_CMD% -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %PS_ARGS%

REM Check exit code
if %errorlevel% neq 0 (
    echo.
    echo Error: Pipeline failed with exit code %errorlevel%
    pause
    exit /b %errorlevel%
)

echo.
echo Pipeline completed successfully!
pause