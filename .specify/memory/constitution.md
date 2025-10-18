<!--
SYNC IMPACT REPORT:
Version: 1.0.0 (Initial constitution)
Added sections:
  - Core Principles (3 principles)
  - Technology Stack Standards
  - Quality Assurance
Templates requiring updates:
  ✅ plan-template.md (Constitution Check section references this document)
  ✅ spec-template.md (User scenarios align with UX principles)
  ✅ tasks-template.md (Task categorization supports all principles)
Follow-up TODOs: None - all placeholders filled
-->

# IdeaFly Constitution

## Core Principles

### I. Diseño Centrado en el Usuario
La experiencia de usuario DEBE ser simple, intuitiva y eficiente. Toda decisión de diseño
y desarrollo DEBE priorizar la reducción de fricción en el proceso creativo. Las interfaces
DEBEN ser responsivas y accesibles siguiendo WCAG. Los componentes de UI DEBEN ser
reutilizables y seguir un sistema de diseño consistente implementado con TailwindCSS.

**Rationale**: Como plataforma SaaS para creativos, la usabilidad directamente impacta 
la productividad y satisfacción del usuario. Una experiencia frustrante resulta en 
abandono del producto.

### II. Escalabilidad y Rendimiento
La arquitectura DEBE estar diseñada para escalar desde un único usuario hasta grandes
equipos. El backend DEBE usar async/await para todas las operaciones de E/S y optimizar
consultas a la base de datos. El frontend DEBE aprovechar Next.js (code-splitting, 
generación estática) para tiempos de carga rápidos.

**Rationale**: El modelo SaaS requiere soportar crecimiento exponencial de usuarios
sin degradación del rendimiento. La latencia alta mata la experiencia creativa.

### III. Código Modular y Mantenible (NON-NEGOTIABLE)
Todo código DEBE seguir principios SOLID y Clean Architecture. Backend DEBE implementar
arquitectura por capas (Controladores, Servicios, Repositorios). Frontend DEBE separar
claramente lógica (hooks), UI (componentes) y gestión de estado. El código DEBE ser
autodocumentado con type hints (Python) y tipado fuerte (TypeScript).

**Rationale**: La mantenibilidad a largo plazo es crítica para un producto SaaS.
El código legacy genera deuda técnica que ralentiza el desarrollo de nuevas funcionalidades.

## Technology Stack Standards

**Monorepo Structure**: `/backend` (Python/FastAPI) y `/frontend` (TypeScript/Next.js/React)
**Database**: PostgreSQL con optimización de consultas obligatoria
**Styling**: TailwindCSS para consistencia visual
**Communication**: API REST con DTOs validados (Pydantic/TypeScript interfaces)

**Code Quality Standards**:
- Backend: PEP 8 estricto, type hints obligatorios, documentación para lógica compleja
- Frontend: ESLint/Prettier, tipado fuerte, evitar `any`, componentes funcionales con Hooks
- API: Endpoints RESTful, modelos Pydantic para validación

## Quality Assurance

**Testing Requirements**:
- Backend: Pruebas unitarias obligatorias para lógica de negocio (pytest), pruebas de
  integración para endpoints críticos
- Frontend: Pruebas unitarias para hooks/utilidades complejas, pruebas de componentes
  para UI crítica (Vitest/Jest + React Testing Library)

**Performance Standards**:
- Backend: Operaciones de E/O no bloqueantes, consultas DB optimizadas
- Frontend: Aprovechamiento completo de Next.js para optimización de carga

**Accessibility**: Cumplimiento WCAG para garantizar usabilidad universal

## Governance

Esta constitución supersede todas las demás prácticas de desarrollo. Todas las Pull
Requests DEBEN verificar cumplimiento con estos principios. Las enmiendas requieren
documentación completa, aprobación del equipo y plan de migración.

**Amendment Process**: Cambios MAJOR requieren redefinición de principios fundamentales.
Cambios MINOR añaden nuevos principios o expanden guidance. Cambios PATCH clarifican
o refinan sin impacto semántico.

**Compliance Review**: Todo PR debe incluir verificación de adherencia a principios.
La complejidad debe ser justificada explícitamente cuando se desvíe de la simplicidad.

**Version**: 1.0.0 | **Ratified**: 2025-10-18 | **Last Amended**: 2025-10-18
