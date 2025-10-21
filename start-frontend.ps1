# ⚛️ Start Frontend Only
# Inicia solo el servidor Next.js

Write-Host "⚛️ Iniciando Frontend (Next.js)..." -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# Cambiar al directorio frontend
Set-Location "frontend"

# Verificar que node_modules existe
Write-Host "📦 Verificando dependencias..." -ForegroundColor Yellow
if (!(Test-Path "node_modules")) {
    Write-Host "❌ node_modules no encontrado. Instalando dependencias..." -ForegroundColor Red
    npm install
}

# Verificar archivo .env.local
if (!(Test-Path ".env.local")) {
    Write-Host "⚠️ Archivo .env.local no encontrado, copiando desde .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env.local"
    Write-Host "📝 Configura las variables en .env.local antes de usar OAuth" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🚀 Iniciando servidor Next.js..." -ForegroundColor Green
Write-Host "   📍 URL: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   🎯 Asegúrate de que el backend esté ejecutándose en :8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️ Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor de desarrollo
npm run dev