@echo off
TITLE TalentLens Demo Launcher
echo ==============================================================
echo           TalentLens - Academic Presentation Launcher
echo ==============================================================
echo.
set OPENBLAS_NUM_THREADS=1
set MKL_NUM_THREADS=1
set OMP_NUM_THREADS=1

echo Starting Student Portal (Port 5000)...
start "TalentLens - Student Portal (Port 5000)" cmd /k "set OPENBLAS_NUM_THREADS=1 && .\venv\Scripts\python.exe backend\app.py"

echo Starting Admin / Instructor Portal (Port 5001)...
start "TalentLens - Admin Portal (Port 5001)" cmd /k "set OPENBLAS_NUM_THREADS=1 && .\venv\Scripts\python.exe backend\admin_app.py"

echo.
echo ==============================================================
echo Both servers have been launched in separate console windows!
echo.
echo Student Portal:   http://127.0.0.1:5000
echo Admin Portal:     http://127.0.0.1:5001
echo.
echo Press any key to exit this launcher window...
echo ==============================================================
pause >nul
