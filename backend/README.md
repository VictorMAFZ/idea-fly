# IdeaFly Backend - Sistema de Autenticación

Backend de la plataforma IdeaFly implementado con FastAPI siguiendo principios Clean Architecture.

## Estructura del Proyecto

```
backend/
├── src/
│   ├── auth/                    # Dominio de autenticación
│   │   ├── __init__.py
│   │   ├── models.py           # Modelos SQLAlchemy (User, OAuth profiles)
│   │   ├── schemas.py          # Esquemas Pydantic (DTOs)
│   │   ├── repository.py       # Capa de acceso a datos
│   │   ├── service.py          # Lógica de negocio
│   │   ├── oauth_service.py    # Servicio OAuth (Google)
│   │   └── router.py           # Endpoints FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuración de entorno
│   │   ├── database.py         # Conexión y sesiones de BD
│   │   ├── security.py         # Utilidades JWT y hashing
│   │   ├── exceptions.py       # Manejo de errores
│   │   └── logging.py          # Configuración de logs
│   └── dependencies/
│       ├── __init__.py
│       └── auth.py             # Dependencias de autenticación
├── tests/
│   ├── auth/                   # Tests del dominio auth
│   └── conftest.py             # Configuración de pytest
├── .env                        # Variables de entorno (NO versionar)
├── .env.example               # Plantilla de variables de entorno
└── requirements.txt           # Dependencias de Python
├── alembic/                    # Migraciones de BD
└── main.py                     # Aplicación FastAPI principal
```

## Tecnologías

- **FastAPI**: Framework web moderno para APIs
- **SQLAlchemy**: ORM para PostgreSQL
- **Pydantic**: Validación de datos y serialización
- **Alembic**: Migraciones de base de datos
- **python-jose**: JWT tokens
- **passlib**: Hashing de contraseñas
- **pytest**: Testing framework

## Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y configura las variables:

```bash
# En el directorio backend/
cp .env.example .env
```

#### Variables Requeridas:

- `JWT_SECRET_KEY`: Clave secreta para JWT (genera una segura)
- `DATABASE_URL`: URL de conexión PostgreSQL
- `GOOGLE_CLIENT_ID`: ID de cliente Google OAuth
- `GOOGLE_CLIENT_SECRET`: Secret de cliente Google OAuth

#### Variables Opcionales:

- `API_PORT`: Puerto del servidor (default: 8000)
- `JWT_EXPIRE_MINUTES`: Expiración de tokens (default: 30)
- `BCRYPT_ROUNDS`: Rounds de hashing bcrypt (default: 12)

### Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar base de datos PostgreSQL
4. Ejecutar migraciones:
```bash
alembic upgrade head
```

5. Iniciar servidor de desarrollo:
```bash
uvicorn src.main:app --reload
```

## Próximos Pasos

1. ✅ Estructura del proyecto creada
2. ✅ Dependencias configuradas
3. ✅ Variables de entorno configuradas
4. ⏳ Implementar modelos y esquemas de datos
5. ⏳ Crear servicios de autenticación
6. ⏳ Implementar endpoints de la API
7. ⏳ Configurar tests unitarios e integración

## Arquitectura

Sigue los principios **Clean Architecture**:
- **Modelos**: Entidades de dominio (SQLAlchemy)
- **Repositorios**: Acceso a datos abstraído
- **Servicios**: Lógica de negocio pura
- **Routers**: Controladores HTTP (FastAPI)
- **Dependencies**: Inyección de dependencias