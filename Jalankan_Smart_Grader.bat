@echo off
title Smart Exam Grader - MA Salafiyah Bantarsari
cd /d "%~dp0"

echo ========================================================
echo   Smart Exam Grader - AnBuso Auto-Filler
echo   MA Salafiyah Bantarsari
echo ========================================================
echo.

:: 1. Deteksi Python yang benar-benar bisa mengeksekusi kode (bukan Microsoft Store dummy stub)
set "PY_CMD="

if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
    "%LocalAppData%\Programs\Python\Python311\python.exe" -c "exit(0)" >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_CMD=%LocalAppData%\Programs\Python\Python311\python.exe"
        goto :PYTHON_READY
    )
)

if exist "%LocalAppData%\Programs\Python\Python310\python.exe" (
    "%LocalAppData%\Programs\Python\Python310\python.exe" -c "exit(0)" >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_CMD=%LocalAppData%\Programs\Python\Python310\python.exe"
        goto :PYTHON_READY
    )
)

if exist "%ProgramFiles%\Python311\python.exe" (
    "%ProgramFiles%\Python311\python.exe" -c "exit(0)" >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_CMD=%ProgramFiles%\Python311\python.exe"
        goto :PYTHON_READY
    )
)

if exist "C:\Python311\python.exe" (
    "C:\Python311\python.exe" -c "exit(0)" >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_CMD=C:\Python311\python.exe"
        goto :PYTHON_READY
    )
)

:: Cek Python Launcher resmi (py.exe)
py -3 -c "exit(0)" >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py -3"
    goto :PYTHON_READY
)

:: Cek perintah 'python' di system PATH dengan tes eksekusi kode nyata (bukan sekadar 'where python')
python -c "import sys; exit(0)" >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :PYTHON_READY
)

:: JIKA BELUM ADA: Lakukan instalasi Python otomatis
echo [INFO] Python resmi belum terdeteksi di komputer ini.

:: Cek apakah file installer lokal sudah ada di folder aplikasi (offline)
if exist "%~dp0assets\prerequisites\python-3.11.9-amd64.exe" (
    echo [INFO] Memasang Python 3.11 dari paket aplikasi offline...
    "%~dp0assets\prerequisites\python-3.11.9-amd64.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1
    goto :VERIFY_INSTALL
)

:: Jika tidak ada installer offline, unduh otomatis via PowerShell
echo [INFO] Mengunduh Python 3.11 resmi dari python.org...
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe', '%temp%\python-3.11.9-installer.exe')"

if exist "%temp%\python-3.11.9-installer.exe" (
    echo [INFO] Memasang Python 3.11 secara otomatis, mohon tunggu sebentar...
    "%temp%\python-3.11.9-installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1
    del /f /q "%temp%\python-3.11.9-installer.exe"
)

:VERIFY_INSTALL
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
    set "PY_CMD=%LocalAppData%\Programs\Python\Python311\python.exe"
    echo [INFO] Python 3.11 berhasil terpasang!
    goto :PYTHON_READY
)

echo [ERROR] Gagal memasang Python secara otomatis.
echo Silakan unduh dan pasang Python 3.11 dari https://www.python.org
echo Pastikan mencentang "Add python.exe to PATH" saat instalasi.
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
