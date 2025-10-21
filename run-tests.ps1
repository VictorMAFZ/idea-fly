# 🧪 Run All Tests
# Ejecuta tests del backend y frontend

Write-Host "🧪 Ejecutando Tests del Sistema de Autenticación" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

$totalErrors = 0

Write-Host ""
Write-Host "🐍 TESTS DEL BACKEND" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

# Cambiar al directorio backend y activar entorno virtual
Set-Location "backend"
& ".\venv\Scripts\Activate.ps1"

# Ejecutar tests específicos de OAuth
Write-Host ""
Write-Host "🔐 Tests de OAuth Service (T048)..." -ForegroundColor Yellow
try {
    python -m pytest tests/auth/test_oauth_service.py -v
    if ($LASTEXITCODE -ne 0) { $totalErrors++ }
} catch {
    Write-Host "❌ Error ejecutando tests de OAuth Service" -ForegroundColor Red
    $totalErrors++
}

Write-Host ""
Write-Host "🔄 Tests de OAuth Flow (T049)..." -ForegroundColor Yellow
try {
    python -m pytest tests/auth/test_oauth_flow.py -v
    if ($LASTEXITCODE -ne 0) { $totalErrors++ }
} catch {
    Write-Host "❌ Error ejecutando tests de OAuth Flow" -ForegroundColor Red
    $totalErrors++
}

Write-Host ""
Write-Host "📊 Todos los tests de autenticación..." -ForegroundColor Yellow
try {
    python -m pytest tests/auth/ -v
    if ($LASTEXITCODE -ne 0) { $totalErrors++ }
} catch {
    Write-Host "❌ Error ejecutando tests de autenticación" -ForegroundColor Red
    $totalErrors++
}

Write-Host ""
Write-Host "⚛️ TESTS DEL FRONTEND" -ForegroundColor Cyan  
Write-Host "=====================" -ForegroundColor Cyan

# Cambiar al directorio frontend
Set-Location "..\frontend"

Write-Host ""
Write-Host "🔘 Tests del componente GoogleAuthButton (T050)..." -ForegroundColor Yellow
try {
    npm test -- GoogleAuthButton.test.tsx
    if ($LASTEXITCODE -ne 0) { $totalErrors++ }
} catch {
    Write-Host "❌ Error ejecutando tests del componente GoogleAuthButton" -ForegroundColor Red
    $totalErrors++
}

Write-Host ""
Write-Host "📊 Todos los tests del frontend..." -ForegroundColor Yellow
try {
    npm test
    if ($LASTEXITCODE -ne 0) { $totalErrors++ }
} catch {
    Write-Host "❌ Error ejecutando tests del frontend" -ForegroundColor Red
    $totalErrors++
}

Write-Host ""
Write-Host "📊 RESUMEN DE TESTS" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

if ($totalErrors -eq 0) {
    Write-Host "✅ ¡Todos los tests pasaron correctamente!" -ForegroundColor Green
    Write-Host "🎉 El sistema está listo para producción" -ForegroundColor Green
} else {
    Write-Host "❌ Se encontraron $totalErrors errores en los tests" -ForegroundColor Red
    Write-Host "🔧 Revisa los logs anteriores para más detalles" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Cobertura implementada:" -ForegroundColor Cyan
Write-Host "  • T048: Unit tests para OAuth service (22 tests)" -ForegroundColor Gray
Write-Host "  • T049: Integration tests para OAuth flow (21 tests)" -ForegroundColor Gray  
Write-Host "  • T050: Component tests para GoogleAuthButton (31 tests)" -ForegroundColor Gray
Write-Host "  • Total: 74 casos de prueba implementados" -ForegroundColor Gray

# Regresar al directorio raíz
Set-Location ".."

exit $totalErrors