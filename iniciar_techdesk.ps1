# Limpiar consola y mostrar banner
Clear-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TechDesk Inventory - Verificacion HAM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar si Python está instalado
Write-Host "[INFO]: Verificando instalacion de Python..." -ForegroundColor Yellow
if (!(Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR]: Python no esta instalado o no esta en el PATH del sistema." -ForegroundColor Red
    Write-Host "Por favor, instale Python y asegurese de marcar la opcion 'Add Python to PATH'." -ForegroundColor Yellow
    Read-Host -Prompt "Presione Enter para salir"
    exit
}
Write-Host "[OK]: Python detectado correctamente." -ForegroundColor Green

# 2. Verificar e instalar requerimientos (Flask)
Write-Host "[INFO]: Verificando dependencias (Flask)..." -ForegroundColor Yellow
python -c "import flask" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[AVISO]: Falta la libreria Flask. Instalando dependencias automaticamente..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    python -m pip install flask
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR]: No se pudo instalar Flask automaticamente. Verifique su conexion a internet." -ForegroundColor Red
        Read-Host -Prompt "Presione Enter para salir"
        exit
    }
    Write-Host "[EXITO]: Flask instalado correctamente." -ForegroundColor Green
} else {
    Write-Host "[OK]: Dependencia Flask ya se encuentra instalada." -ForegroundColor Green
}

# 3. Verificar si la base de datos existe, si no, crearla
if (!(Test-Path "inventory.db")) {
    Write-Host "[INFO]: Base de datos no encontrada. Inicializando por primera vez..." -ForegroundColor Yellow
    python init_db.py
} else {
    Write-Host "[OK]: Base de datos detectada." -ForegroundColor Green
}

# 4. Iniciar Flask en segundo plano
Write-Host "[INFO]: Levantando servidor web en Flask..." -ForegroundColor Cyan
$flaskJob = Start-Process python -ArgumentList "app.py" -PassThru -NoNewWindow

# 5. Esperar exactamente 3 segundos para que cargue bien
Write-Host "[INFO]: Esperando 3 segundos para asegurar la carga del servidor..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 6. Abrir el navegador predeterminado
Write-Host "[INFO]: Abriendo navegador en http://127.0.0.1:5000..." -ForegroundColor Green
Start-Process "http://127.0.0.1:5000"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " [EXITO]: Sistema en ejecucion." -ForegroundColor Green
Write-Host " No cierre esta ventana mientras use la app." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Mantener la consola abierta mientras Flask corre
$flaskJob.WaitForExit()