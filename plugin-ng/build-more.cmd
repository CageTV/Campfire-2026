@echo off
rem Builds the extra targets (Frostfall regular + ESL, Last Seed) on the already built CommonLib. Output: build\release\out\<target>\<name>.dll
setlocal
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
set VCPKG_ROOT=C:\vcpkg
cd /d "%~dp0"
cmake --preset release || exit /b 1
cmake --build --preset release --target FrostfallRegular FrostfallESL LastSeed || exit /b 1
