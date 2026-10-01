@echo off
title Build Installer - Smart Exam Grader
cd /d "%~dp0"

echo ========================================================
echo   Building Setup_SmartExamGrader_v1.0.0.exe
echo ========================================================
echo.

set "ISCC_PATH=C:\Users\black\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_PATH%" (
    where iscc >nul 2>&1
    if %errorlevel% equ 0 (
        set "ISCC_PATH=iscc"
    ) else (
        echo [ERROR] Inno Setup Compiler (ISCC.exe) tidak ditemukan!
        pause
        exit /b
    )
)

echo [INFO] Mengompilasi installer.iss...
"%ISCC_PATH%" installer.iss

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo   [SUKSES] Installer berhasil dibuat di folder dist\
    echo   File: dist\Setup_SmartExamGrader_v1.0.0.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] Gagal mengompilasi installer.
)

pause
