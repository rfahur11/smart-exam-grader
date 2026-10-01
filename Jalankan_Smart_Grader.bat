@echo off
title Smart Exam Grader - MA Salafiyah Bantarsari
cd /d "%~dp0"

echo ========================================================
echo   Smart Exam Grader & AnBuso Auto-Filler
echo   MA Salafiyah Bantarsari
echo ========================================================
echo.

:: 1. Deteksi Python (system PATH, py launcher, atau local path)
set "PY_CMD="
where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :PYTHON_READY
)
where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py"
    goto :PYTHON_READY
)
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
    set "PY_CMD=%LocalAppData%\Programs\Python\Python311\python.exe"
    goto :PYTHON_READY
)
if exist "%LocalAppData%\Programs\Python\Python310\python.exe" (
    set "PY_CMD=%LocalAppData%\Programs\Python\Python310\python.exe"
    goto :PYTHON_READY
)

:: Jika belum ada, otomatis download & install Python 3.11 silent
echo [INFO] Python belum terdeteksi di sistem ini.
echo [INFO] Mengunduh Python 3.11 resmi dari python.org...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe', '%temp%\python-3.11.9-installer.exe')"
if exist "%temp%\python-3.11.9-installer.exe" (
    echo [INFO] Memasang Python 3.11 secara otomatis (mohon tunggu sebentar)...
    "%temp%\python-3.11.9-installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    del "%temp%\python-3.11.9-installer.exe"
    if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
        set "PY_CMD=%LocalAppData%\Programs\Python\Python311\python.exe"
        echo [INFO] Python 3.11 berhasil terpasang!
        goto :PYTHON_READY
    )
)

echo [ERROR] Gagal menginstall Python otomatis.
echo Silakan install Python 3.10 atau 3.11 manual dari https://www.python.org/downloads/
echo (Pastikan centang "Add python.exe to PATH").
echo.
pause
exit /b

:PYTHON_READY
:: 2. Setup Virtual Environment otomatis jika belum ada
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Menyiapkan environment pertama kali... Ini hanya berjalan sekali.
    %PY_CMD% -m venv .venv
    call .venv\Scripts\activate.bat
    echo [INFO] Menginstall dependensi (Streamlit, OpenCV, RapidOCR, pywin32)...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo [INFO] Setup selesai!
    echo.
) else (
    call .venv\Scripts\activate.bat
)


:: 3. Jalankan aplikasi Streamlit
echo [INFO] Membuka dashboard antarmuka guru...
start http://localhost:8501
streamlit run app.py --server.headless false --server.port 8501

pause

