# Frontend - IdeaFly Authentication System

Frontend application built with Next.js and React for the IdeaFly authentication system.

## Project Structure

```
frontend/src/
├── components/
│   └── auth/          # Authentication-related components
│       └── index.ts   # Barrel exports for auth components
├── contexts/          # React Context providers
│   └── index.ts       # Barrel exports for contexts
├── hooks/             # Custom React hooks
│   └── index.ts       # Barrel exports for hooks  
├── services/          # API service functions
│   └── index.ts       # Barrel exports for services
└── types/             # TypeScript type definitions
    └── index.ts       # Barrel exports for types
```

## Technology Stack

- **Next.js 14+**: React framework with App Router
- **React 18+**: UI library
- **TypeScript**: Type safety
- **TailwindCSS**: Styling framework
- **@react-oauth/google**: Google OAuth integration
- **axios**: HTTP client

## Development Notes

This structure follows Clean Architecture principles with clear separation of concerns:

- **Components**: Reusable UI components, organized by feature
- **Contexts**: Global state management with React Context
- **Hooks**: Custom business logic and state management
- **Services**: API communication and external service integration
- **Types**: TypeScript interfaces and type definitions

Each directory includes an `index.ts` file for barrel exports to simplify imports throughout the application.

## Configuration

### Environment Variables

The frontend uses Next.js environment variables with the `NEXT_PUBLIC_` prefix for client-side access.

Copy `.env.example` to `.env.local` and configure:

```bash
# En el directorio frontend/
cp .env.example .env.local
```

#### Required Variables:

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID`: Google OAuth Client ID

#### Optional Variables:

- `NEXT_PUBLIC_DEBUG_MODE`: Enable debug logging (default: true)
- `NEXT_PUBLIC_SESSION_TIMEOUT`: Session timeout in milliseconds (default: 1800000)
- `NEXT_PUBLIC_THEME`: UI theme (default: light)

### Installation and Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables (see above)

3. Start development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
npm start
```

### Scripts Available

- `npm run dev`: Start development server
- `npm run build`: Build production bundle
- `npm run start`: Start production server
- `npm run lint`: Run ESLint
- `npm run type-check`: TypeScript type checking
- `npm test`: Run tests with Vitest
- `npm run test:watch`: Run tests in watch mode

## API Integration

The frontend communicates with the FastAPI backend through:

- **Base URL**: Configured via `NEXT_PUBLIC_API_URL`
- **Authentication**: JWT tokens stored in localStorage
- **HTTP Client**: Axios with automatic token injection
- **Error Handling**: Global error interceptors