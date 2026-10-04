@echo off
rem Headless build against alandtse's CommonLibSSE-NG. Output: build\release\Campfire.dll (+ .pdb). The first build compiles CommonLib (~15 min).
setlocal
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
set VCPKG_ROOT=C:\vcpkg
cd /d "%~dp0"
cmake --preset release || exit /b 1
cmake --build --preset release || exit /b 1
