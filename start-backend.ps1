# 🐍 Start Backend Only
# Inicia solo el servidor FastAPI

Write-Host "🐍 Iniciando Backend (FastAPI)..." -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Cambiar al directorio backend
Set-Location "backend"

# Activar entorno virtual
Write-Host "⚙️ Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Verificar que las dependencias estén instaladas
Write-Host "📦 Verificando dependencias..." -ForegroundColor Yellow
if (!(Test-Path "venv\Lib\site-packages\fastapi")) {
    Write-Host "❌ FastAPI no está instalado. Instalando dependencias..." -ForegroundColor Red
    pip install -r requirements.txt
}

# Verificar archivo .env
if (!(Test-Path ".env")) {
    Write-Host "⚠️ Archivo .env no encontrado, copiando desde .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Configura las variables en .env antes de usar OAuth" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🚀 Iniciando servidor FastAPI..." -ForegroundColor Green
Write-Host "   📍 URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   📚 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   🔍 ReDoc: http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️ Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor con hot-reload
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000