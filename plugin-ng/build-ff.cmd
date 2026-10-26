@echo off
setlocal
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
set VCPKG_ROOT=C:\vcpkg
cd /d "%~dp0"
cmake --build build\release --target %* -- -k 0
