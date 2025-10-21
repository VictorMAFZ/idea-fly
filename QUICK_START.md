# 🚀 IdeaFly - Inicialización Rápida

## Opciones de Inicialización

### 🎯 Método Rápido (Recomendado)
```bash
# Script interactivo con todas las opciones
.\start.ps1
```

### 🔧 Métodos Específicos

#### 🐍 Solo Backend (FastAPI)
```bash
.\start-backend.ps1
```
**Acceso:** http://localhost:8000  
**Documentación:** http://localhost:8000/docs

#### ⚛️ Solo Frontend (Next.js)  
```bash
.\start-frontend.ps1
```
**Acceso:** http://localhost:3000

#### 🧪 Ejecutar Tests
```bash
.\run-tests.ps1
```

### 🛠️ Métodos Manuales

#### Backend Manual
```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Manual
```bash
cd frontend
npm run dev
```

## 📋 Requisitos Previos

### ✅ Verificaciones Automáticas
Los scripts verifican automáticamente:
- ✅ Entorno virtual de Python (`backend/venv/`)
- ✅ Dependencias de Node.js (`frontend/node_modules/`)
- ✅ Archivos de configuración (`.env`, `.env.local`)

### 🔧 Si algo falla, ejecuta:

#### Python/Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Node.js/Frontend
```bash
cd frontend
npm install
```

### ⚙️ Configuración de Variables

#### Backend (`.env`)
```env
# Base configuration
DATABASE_URL=sqlite:///./ideafly.db
SECRET_KEY=tu-clave-secreta-aqui

# Google OAuth (obligatorio para login)
GOOGLE_CLIENT_ID=tu-google-client-id
GOOGLE_CLIENT_SECRET=tu-google-client-secret

# Environment
ENVIRONMENT=development
```

#### Frontend (`.env.local`)
```env
# API URLs
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=tu-google-client-id
```

## 🎯 URLs de Desarrollo

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:3000 | Aplicación Next.js |
| **Backend API** | http://localhost:8000 | API FastAPI |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **ReDoc** | http://localhost:8000/redoc | Documentación alternativa |

## 🧪 Testing

### 📊 Cobertura de Tests Actual
- **T048:** OAuth Service Unit Tests (22 tests) ✅
- **T049:** OAuth Flow Integration Tests (21 tests) ✅  
- **T050:** GoogleAuthButton Component Tests (31 tests) ✅
- **Total:** 74 casos de prueba implementados

### 🔍 Comandos de Test
```bash
# Todos los tests
.\run-tests.ps1

# Solo backend
cd backend && python -m pytest tests/ -v

# Solo frontend  
cd frontend && npm test

# Tests específicos
cd backend && python -m pytest tests/auth/test_oauth_service.py -v
cd frontend && npm test GoogleAuthButton.test.tsx
```

## 🔧 Desarrollo

### 🌟 Características Implementadas
- ✅ **Autenticación Google OAuth 2.0**
- ✅ **JWT Token Management**
- ✅ **User Registration/Login**
- ✅ **Protected Routes**
- ✅ **Database Integration (SQLAlchemy)**
- ✅ **Comprehensive Testing Suite**

### 🏗️ Arquitectura
```
IdeaFly/
├── backend/          # FastAPI + SQLAlchemy + PostgreSQL
│   ├── src/         # Código fuente
│   ├── tests/       # Tests (pytest)
│   └── alembic/     # Migraciones de DB
├── frontend/         # Next.js + TypeScript + Tailwind
│   ├── src/         # Componentes y páginas
│   └── tests/       # Tests (Vitest + RTL)
└── scripts/          # Scripts de inicialización
```

### 📝 Próximos Pasos
1. Configura las variables de OAuth en `.env` y `.env.local`
2. Ejecuta `.\start.ps1` para inicializar
3. Accede a http://localhost:3000 para probar la aplicación
4. Revisa http://localhost:8000/docs para la documentación de la API

## 🆘 Resolución de Problemas

### ❌ "ModuleNotFoundError"
```bash
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### ❌ "npm command not found"
Instala Node.js desde https://nodejs.org/

### ❌ "Puerto ya en uso"
- Backend: Cambia el puerto en el comando uvicorn `--port 8001`
- Frontend: Usa `npm run dev -- -p 3001`

### ❌ "OAuth no funciona"
1. Verifica `GOOGLE_CLIENT_ID` en ambos `.env` y `.env.local`
2. Configura las URLs de redirect en Google Console
3. Asegúrate de que ambos servicios estén ejecutándose

## 🎉 ¡Listo para Desarrollo!

El sistema está completamente configurado con autenticación OAuth, tests comprehensivos y documentación automática. ¡Comienza a desarrollar tus ideas! 🚀