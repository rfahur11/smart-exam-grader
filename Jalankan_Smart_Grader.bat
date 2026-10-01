@echo off
title Smart Exam Grader - MA Salafiyah Bantarsari
cd /d "%~dp0"

echo ========================================================
echo   Smart Exam Grader - AnBuso Auto-Filler
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
    set "PY_CMD=py -3"
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

if exist "C:\Python311\python.exe" (
    set "PY_CMD=C:\Python311\python.exe"
    goto :PYTHON_READY
)

:: Jika belum ada Python sama sekali, otomatis unduh & pasang Python 3.11 silent
echo [INFO] Python belum terdeteksi di komputer ini.
echo [INFO] Mengunduh installer Python 3.11 resmi dari python.org...
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe', '%temp%\python-3.11.9-installer.exe')"

if not exist "%temp%\python-3.11.9-installer.exe" (
    echo [ERROR] Gagal mengunduh installer Python otomatis.
    echo Pastikan komputer terhubung ke internet.
    pause
    exit /b
)

echo [INFO] Memasang Python 3.11 secara otomatis, mohon tunggu...
"%temp%\python-3.11.9-installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
del /f /q "%temp%\python-3.11.9-installer.exe"

if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
    set "PY_CMD=%LocalAppData%\Programs\Python\Python311\python.exe"
    echo [INFO] Python 3.11 berhasil dipasang!
    goto :PYTHON_READY
)

echo [ERROR] Python tetap tidak terdeteksi setelah instalasi.
echo Silakan install Python 3.10 atau 3.11 manual dari https://www.python.org
pause
exit /b

:PYTHON_READY
:: 2. Setup Virtual Environment otomatis jika belum ada
if not exist "%~dp0.venv\Scripts\activate.bat" (
    echo [INFO] Menyiapkan environment pertama kali. Tahap ini hanya berjalan sekali...
    "%PY_CMD%" -m venv "%~dp0.venv"
    if not exist "%~dp0.venv\Scripts\activate.bat" (
        echo [ERROR] Gagal membuat virtual environment .venv
        pause
        exit /b
    )
    call "%~dp0.venv\Scripts\activate.bat"
    echo [INFO] Menginstall paket yang dibutuhkan: Streamlit, OpenCV, RapidOCR, pywin32...
    python -m pip install --upgrade pip
    pip install -r "%~dp0requirements.txt"
    echo [INFO] Seluruh dependensi berhasil dipasang!
    echo.
) else (
    call "%~dp0.venv\Scripts\activate.bat"
    :: Cek apakah streamlit sudah terpasang di venv, jika belum lakukan pip install
    if not exist "%~dp0.venv\Scripts\streamlit.exe" (
        echo [INFO] Memperbarui paket dependensi di .venv...
        pip install -r "%~dp0requirements.txt"
    )
)

:: 3. Jalankan aplikasi Streamlit (Streamlit otomatis membuka browser)
echo [INFO] Membuka dashboard Smart Exam Grader di browser...

if exist "%~dp0.venv\Scripts\streamlit.exe" (
    "%~dp0.venv\Scripts\streamlit.exe" run "%~dp0app.py" --server.headless false
) else (
    streamlit run "%~dp0app.py" --server.headless false
)

pause
