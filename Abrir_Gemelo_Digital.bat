@echo off
color 0B
echo ========================================================
echo        GEMELO DIGITAL APH MONTERIA - SIMULADOR
echo ========================================================
echo.
echo Iniciando el sistema... Por favor espere.
echo.

:: Comprobar si Python esta instalado
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] No se encontro Python en este computador.
    echo Por favor, instale Python desde python.org asegurandose de marcar la casilla "Add Python to PATH".
    pause
    exit /b
)

:: Comprobar si existe el entorno virtual, si no, crearlo
IF NOT EXIST ".venv\Scripts\activate.bat" (
    echo [INFO] Primera vez ejecutando. Preparando el motor (esto puede tardar unos minutos)...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r packages.txt
) ELSE (
    call .venv\Scripts\activate.bat
)

echo [INFO] Todo listo. Abriendo la aplicacion en su navegador...
streamlit run app_ambulancias\app.py

pause
