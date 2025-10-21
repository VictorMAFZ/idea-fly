/**
 * Dashboard Page for IdeaFly Application.
 * 
 * Main dashboard page for authenticated users showing their ideas and
 * account information with the header containing logout functionality.
 */

'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useIsAuthenticated, useCurrentUser } from '../../hooks/useAuth';
import { Header } from '../../components/layout';

export default function DashboardPage() {
  const router = useRouter();
  const isAuthenticated = useIsAuthenticated();
  const user = useCurrentUser();

  // Redirect to login if not authenticated
  React.useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Show loading while checking authentication
  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with logout functionality */}
      <Header />
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome Section */}
          <div className="bg-white overflow-hidden shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                ¡Bienvenido, {user.name}!
              </h1>
              <p className="text-gray-600">
                Este es tu dashboard personal donde puedes gestionar tus ideas y proyectos.
              </p>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total Ideas
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        12
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Ideas Completadas
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        3
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-8 w-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        En Progreso
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        9
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Ideas */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Ideas Recientes
              </h2>
              <div className="space-y-4">
                <div className="border-l-4 border-blue-400 pl-4">
                  <h3 className="text-sm font-medium text-gray-900">
                    App de Productividad
                  </h3>
                  <p className="text-sm text-gray-500">
                    Una aplicación móvil para gestionar tareas y aumentar la productividad personal.
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Creada hace 2 días
                  </p>
                </div>
                
                <div className="border-l-4 border-green-400 pl-4">
                  <h3 className="text-sm font-medium text-gray-900">
                    Plataforma de E-learning
                  </h3>
                  <p className="text-sm text-gray-500">
                    Sistema de cursos online con gamificación y seguimiento de progreso.
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Creada hace 1 semana
                  </p>
                </div>
                
                <div className="border-l-4 border-purple-400 pl-4">
                  <h3 className="text-sm font-medium text-gray-900">
                    Red Social para Desarrolladores
                  </h3>
                  <p className="text-sm text-gray-500">
                    Plataforma para que desarrolladores compartan código y colaboren en proyectos.
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Creada hace 2 semanas
                  </p>
                </div>
              </div>
              
              <div className="mt-6">
                <button
                  onClick={() => router.push('/ideas')}
                  className="text-blue-600 hover:text-blue-500 text-sm font-medium"
                >
                  Ver todas las ideas →
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}