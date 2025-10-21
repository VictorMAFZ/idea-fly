#!/bin/bash
# 🚀 IdeaFly Startup Script (Bash version for Git Bash/WSL)

echo "🚀 Iniciando IdeaFly - Sistema de Autenticación"
echo "============================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "backend/src/main.py" ]; then
    echo "❌ Error: No se encuentra backend/src/main.py"
    echo "   Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: No se encuentra frontend/package.json"
    echo "   Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

echo ""
echo "📋 Verificando dependencias..."

# Verificar entorno virtual de Python
echo "🐍 Verificando entorno virtual de Python..."
if [ -f "backend/venv/bin/activate" ] || [ -f "backend/venv/Scripts/activate" ]; then
    echo "   ✅ Entorno virtual encontrado"
else
    echo "   ❌ Entorno virtual no encontrado en backend/venv/"
    echo "   Ejecuta: cd backend && python -m venv venv"
    exit 1
fi

# Verificar node_modules
echo "📦 Verificando dependencias de Node.js..."
if [ -d "frontend/node_modules" ]; then
    echo "   ✅ node_modules encontrado"
else
    echo "   ❌ node_modules no encontrado"
    echo "   Ejecuta: cd frontend && npm install"
    exit 1
fi

echo ""
echo "🔧 Configurando entornos..."

# Verificar archivos .env
echo "⚙️ Verificando configuración del backend..."
if [ -f "backend/.env" ]; then
    echo "   ✅ backend/.env encontrado"
else
    echo "   ⚠️ backend/.env no encontrado, copiando desde .env.example..."
    cp "backend/.env.example" "backend/.env"
    echo "   📝 Revisa backend/.env y configura las variables necesarias"
fi

echo "⚙️ Verificando configuración del frontend..."
if [ -f "frontend/.env.local" ]; then
    echo "   ✅ frontend/.env.local encontrado"
else
    echo "   ⚠️ frontend/.env.local no encontrado, copiando desde .env.example..."
    cp "frontend/.env.example" "frontend/.env.local"
    echo "   📝 Revisa frontend/.env.local y configura las variables necesarias"
fi

echo ""
echo "🎯 Selecciona el modo de inicio:"
echo "1. 🔥 Iniciar TODO (Backend + Frontend)"
echo "2. 🐍 Solo Backend (FastAPI)"
echo "3. ⚛️ Solo Frontend (Next.js)"
echo "4. 🧪 Ejecutar Tests"
echo "5. ❌ Salir"

read -p "Ingresa tu opción (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🔥 Iniciando Backend + Frontend..."
        echo "   Backend: http://localhost:8000"
        echo "   Frontend: http://localhost:3000"
        echo "   Docs API: http://localhost:8000/docs"
        echo ""
        echo "⚠️ Presiona Ctrl+C para detener ambos servicios"
        echo ""
        
        # Activar entorno virtual y iniciar backend en background
        cd backend
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        else
            source venv/Scripts/activate
        fi
        python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        cd ..
        
        # Iniciar frontend en background
        cd frontend
        npm run dev &
        FRONTEND_PID=$!
        cd ..
        
        echo "🚀 Servicios iniciados!"
        echo "   Backend PID: $BACKEND_PID"
        echo "   Frontend PID: $FRONTEND_PID"
        echo ""
        echo "🛑 Para detener los servicios: kill $BACKEND_PID $FRONTEND_PID"
        
        # Esperar a que termine uno de los procesos
        wait $BACKEND_PID $FRONTEND_PID
        ;;
        
    2)
        echo ""
        echo "🐍 Iniciando solo Backend..."
        echo "   URL: http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
        echo ""
        
        cd backend
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        else
            source venv/Scripts/activate
        fi
        python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
        ;;
        
    3)
        echo ""
        echo "⚛️ Iniciando solo Frontend..."
        echo "   URL: http://localhost:3000"
        echo ""
        
        cd frontend
        npm run dev
        ;;
        
    4)
        echo ""
        echo "🧪 Ejecutando Tests..."
        echo ""
        
        echo "🐍 Tests del Backend:"
        cd backend
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        else
            source venv/Scripts/activate
        fi
        python -m pytest tests/ -v
        
        echo ""
        echo "⚛️ Tests del Frontend:"
        cd ../frontend
        npm test
        ;;
        
    5)
        echo "👋 ¡Hasta luego!"
        exit 0
        ;;
        
    *)
        echo "❌ Opción no válida"
        exit 1
        ;;
esac