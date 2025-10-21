# 🚀 IdeaFly - Startup Script
# Inicialización del Backend (FastAPI) y Frontend (Next.js)

Write-Host "🚀 Iniciando IdeaFly - Sistema de Autenticación" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# Verificar que estamos en el directorio correcto
if (!(Test-Path "backend\src\main.py")) {
    Write-Host "❌ Error: No se encuentra backend\src\main.py" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar este script desde el directorio raíz del proyecto" -ForegroundColor Yellow
    exit 1
}

if (!(Test-Path "frontend\package.json")) {
    Write-Host "❌ Error: No se encuentra frontend\package.json" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar este script desde el directorio raíz del proyecto" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📋 Verificando dependencias..." -ForegroundColor Cyan

# Verificar entorno virtual de Python
Write-Host "🐍 Verificando entorno virtual de Python..." -ForegroundColor Yellow
if (Test-Path "backend\venv\Scripts\Activate.ps1") {
    Write-Host "   ✅ Entorno virtual encontrado" -ForegroundColor Green
} else {
    Write-Host "   ❌ Entorno virtual no encontrado en backend\venv\" -ForegroundColor Red
    Write-Host "   Ejecuta: cd backend && python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Verificar node_modules
Write-Host "📦 Verificando dependencias de Node.js..." -ForegroundColor Yellow
if (Test-Path "frontend\node_modules") {
    Write-Host "   ✅ node_modules encontrado" -ForegroundColor Green
} else {
    Write-Host "   ❌ node_modules no encontrado" -ForegroundColor Red
    Write-Host "   Ejecuta: cd frontend && npm install" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🔧 Configurando entornos..." -ForegroundColor Cyan

# Verificar archivos .env
Write-Host "⚙️ Verificando configuración del backend..." -ForegroundColor Yellow
if (Test-Path "backend\.env") {
    Write-Host "   ✅ backend\.env encontrado" -ForegroundColor Green
} else {
    Write-Host "   ⚠️ backend\.env no encontrado, copiando desde .env.example..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "   📝 Revisa backend\.env y configura las variables necesarias" -ForegroundColor Cyan
}

Write-Host "⚙️ Verificando configuración del frontend..." -ForegroundColor Yellow
if (Test-Path "frontend\.env.local") {
    Write-Host "   ✅ frontend\.env.local encontrado" -ForegroundColor Green
} else {
    Write-Host "   ⚠️ frontend\.env.local no encontrado, copiando desde .env.example..." -ForegroundColor Yellow
    Copy-Item "frontend\.env.example" "frontend\.env.local"
    Write-Host "   📝 Revisa frontend\.env.local y configura las variables necesarias" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🎯 Selecciona el modo de inicio:" -ForegroundColor Cyan
Write-Host "1. 🔥 Iniciar TODO (Backend + Frontend)" -ForegroundColor White
Write-Host "2. 🐍 Solo Backend (FastAPI)" -ForegroundColor White  
Write-Host "3. ⚛️ Solo Frontend (Next.js)" -ForegroundColor White
Write-Host "4. 🧪 Ejecutar Tests" -ForegroundColor White
Write-Host "5. ❌ Salir" -ForegroundColor White

$choice = Read-Host "Ingresa tu opción (1-5)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🔥 Iniciando Backend + Frontend..." -ForegroundColor Green
        Write-Host "   Backend: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Cyan
        Write-Host "   Docs API: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⚠️ Presiona Ctrl+C para detener ambos servicios" -ForegroundColor Yellow
        Write-Host ""
        
        # Iniciar backend en proceso separado
        $backendJob = Start-Job -ScriptBlock {
            Set-Location "D:\victo\proyectos\idea-fly\backend"
            & ".\venv\Scripts\Activate.ps1"
            python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
        }
        
        Start-Sleep -Seconds 3
        
        # Iniciar frontend en proceso separado  
        $frontendJob = Start-Job -ScriptBlock {
            Set-Location "D:\victo\proyectos\idea-fly\frontend"
            npm run dev
        }
        
        Write-Host "🚀 Servicios iniciados!" -ForegroundColor Green
        Write-Host "   Backend Job ID: $($backendJob.Id)" -ForegroundColor Gray
        Write-Host "   Frontend Job ID: $($frontendJob.Id)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "📝 Para ver logs en tiempo real:"
        Write-Host "   Backend: Receive-Job $($backendJob.Id) -Keep"
        Write-Host "   Frontend: Receive-Job $($frontendJob.Id) -Keep"
        Write-Host ""
        Write-Host "🛑 Para detener los servicios:"
        Write-Host "   Stop-Job $($backendJob.Id), $($frontendJob.Id)"
        Write-Host "   Remove-Job $($backendJob.Id), $($frontendJob.Id)"
    }
    
    "2" {
        Write-Host ""
        Write-Host "🐍 Iniciando solo Backend..." -ForegroundColor Green
        Write-Host "   URL: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "   Docs: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host ""
        
        Set-Location "backend"
        & ".\venv\Scripts\Activate.ps1"
        python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    }
    
    "3" {
        Write-Host ""
        Write-Host "⚛️ Iniciando solo Frontend..." -ForegroundColor Green
        Write-Host "   URL: http://localhost:3000" -ForegroundColor Cyan
        Write-Host ""
        
        Set-Location "frontend"
        npm run dev
    }
    
    "4" {
        Write-Host ""
        Write-Host "🧪 Ejecutando Tests..." -ForegroundColor Green
        Write-Host ""
        
        Write-Host "🐍 Tests del Backend:" -ForegroundColor Yellow
        Set-Location "backend"
        & ".\venv\Scripts\Activate.ps1"
        python -m pytest tests/ -v
        
        Write-Host ""
        Write-Host "⚛️ Tests del Frontend:" -ForegroundColor Yellow
        Set-Location "..\frontend"
        npm test
    }
    
    "5" {
        Write-Host "👋 ¡Hasta luego!" -ForegroundColor Green
        exit 0
    }
    
    default {
        Write-Host "❌ Opción no válida" -ForegroundColor Red
        exit 1
    }
}