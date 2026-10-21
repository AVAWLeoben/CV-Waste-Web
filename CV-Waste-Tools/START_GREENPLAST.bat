@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title GreenPlast Tools Launcher

rem Try the active Conda installation first, then common Windows paths.
set "CONDA_BAT="
if defined CONDA_EXE (
    for %%I in ("%CONDA_EXE%") do (
        if exist "%%~dpI..\condabin\conda.bat" set "CONDA_BAT=%%~dpI..\condabin\conda.bat"
    )
)
if not defined CONDA_BAT (
    for /f "delims=" %%I in ('where conda.bat 2^>nul') do (
        if not defined CONDA_BAT set "CONDA_BAT=%%I"
    )
)
if not defined CONDA_BAT if exist "%USERPROFILE%\miniconda3\condabin\conda.bat" set "CONDA_BAT=%USERPROFILE%\miniconda3\condabin\conda.bat"
if not defined CONDA_BAT if exist "%USERPROFILE%\anaconda3\condabin\conda.bat" set "CONDA_BAT=%USERPROFILE%\anaconda3\condabin\conda.bat"
if not defined CONDA_BAT if exist "%USERPROFILE%\miniforge3\condabin\conda.bat" set "CONDA_BAT=%USERPROFILE%\miniforge3\condabin\conda.bat"
if not defined CONDA_BAT if exist "%LOCALAPPDATA%\miniconda3\condabin\conda.bat" set "CONDA_BAT=%LOCALAPPDATA%\miniconda3\condabin\conda.bat"
if not defined CONDA_BAT if exist "%LOCALAPPDATA%\anaconda3\condabin\conda.bat" set "CONDA_BAT=%LOCALAPPDATA%\anaconda3\condabin\conda.bat"
if not defined CONDA_BAT if exist "%ProgramData%\miniconda3\condabin\conda.bat" set "CONDA_BAT=%ProgramData%\miniconda3\condabin\conda.bat"
if not defined CONDA_BAT if exist "%ProgramData%\Anaconda3\condabin\conda.bat" set "CONDA_BAT=%ProgramData%\Anaconda3\condabin\conda.bat"

if not defined CONDA_BAT (
    echo ERROR: Conda was not found.
    echo Install Miniconda, Miniforge or Anaconda first, then double-click this file.
    echo https://docs.conda.io/projects/conda/en/latest/user-guide/install/
    pause
    exit /b 1
)

echo Using Conda launcher: "%CONDA_BAT%"
call "%CONDA_BAT%" activate base
if errorlevel 1 (
    echo ERROR: Could not activate the Conda base environment.
    pause
    exit /b 1
)
rem A few minimal Conda base environments omit Tkinter. Bootstrap from the
rem standard library in that case; the dedicated environment installs tk.
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo Conda base lacks Tkinter. Starting headless environment bootstrap...
    python -u "%~dp0greenplast_bootstrap.py"
) else (
    python -u "%~dp0greenplast_launcher.py"
)
if errorlevel 1 (
    echo.
    echo The GreenPlast launcher exited with an error.
    pause
    exit /b 1
)
exit /b 0
