@echo off
echo Compilando la aplicacion de escritorio a un ejecutable (.exe)...
pyinstaller --onedir --windowed --name "GemeloDigital_Montería" gemelo_digital_desktop.py
echo ========================================
echo Compilacion finalizada.
echo Puedes encontrar tu ejecutable en la carpeta "dist/GemeloDigital_Montería"
echo Asegurate de que el archivo 'accidentes_verificados_actualizados.csv' este en la misma carpeta o en el directorio raiz si lo ejecutas desde alli.
pause
