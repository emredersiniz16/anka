@echo off
:: ============================================================
:: ANKA OS Installer — Windows EXE Derleme Scripti
:: ============================================================
:: Gereksinimler:
::   pip install pyinstaller
::
:: Kullanım:
::   build_exe.bat
::   → AnkaOS_Installer.exe oluşturulur
:: ============================================================

echo.
echo =============================================
echo   ANKA OS Installer - EXE Build
echo =============================================
echo.

:: Python ve PyInstaller kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi. Python 3.8+ yuklu olmali.
    pause
    exit /b 1
)

pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [BİLGİ] PyInstaller yuklenmiyor, kuruluyor...
    pip install pyinstaller
    if errorlevel 1 (
        echo [HATA] PyInstaller kurulamadir.
        pause
        exit /b 1
    )
)

:: Eski build temizle
if exist "dist\AnkaOS_Installer.exe" del /f /q "dist\AnkaOS_Installer.exe"
if exist "build" rmdir /s /q build
if exist "AnkaOS_Installer.spec" del /f /q AnkaOS_Installer.spec

echo [BUILD] PyInstaller calıştırılıyor...

:: --onefile   : tek EXE
:: --windowed  : konsol penceresi açma (GUI uygulama)
:: --name      : EXE adı
:: --icon       : ikon (assets dizinindeyse)
set ICON_OPT=
if exist "..\assets\fly_icon.bmp" (
    :: PyInstaller .ico ister, .bmp değil — ikonu atla
    set ICON_OPT=
)

pyinstaller ^
    --onefile ^
    --windowed ^
    --name AnkaOS_Installer ^
    --add-data ".;." ^
    anka_installer.py

if errorlevel 1 (
    echo.
    echo [HATA] EXE olusturulamadir!
    pause
    exit /b 1
)

echo.
echo =============================================
echo   TAMAMLANDI: dist\AnkaOS_Installer.exe
echo =============================================
echo.

:: dist klasorunden kopyala
if exist "dist\AnkaOS_Installer.exe" (
    copy /y "dist\AnkaOS_Installer.exe" "AnkaOS_Installer.exe"
    echo [OK] AnkaOS_Installer.exe hazir!
)

pause
