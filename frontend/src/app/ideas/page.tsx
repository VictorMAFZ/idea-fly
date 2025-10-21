/**
 * Ideas Page for IdeaFly Application.
 * 
 * Page showing all user ideas with the header containing logout functionality.
 */

'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useIsAuthenticated, useCurrentUser } from '../../hooks/useAuth';
import { Header } from '../../components/layout';

export default function IdeasPage() {
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
          <p className="mt-4 text-gray-600">Cargando ideas...</p>
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
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Mis Ideas</h1>
            <p className="mt-2 text-gray-600">
              Gestiona y desarrolla todas tus ideas en un solo lugar.
            </p>
          </div>

          {/* Ideas Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Idea Card 1 */}
            <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="h-3 w-3 bg-yellow-400 rounded-full mr-2"></div>
                    <span className="text-sm text-gray-500">En Progreso</span>
                  </div>
                  <span className="text-xs text-gray-400">2 días</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  App de Productividad
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  Una aplicación móvil para gestionar tareas y aumentar la productividad personal con técnicas de gamificación.
                </p>
                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    Móvil
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Productividad
                  </span>
                </div>
                <button className="text-blue-600 hover:text-blue-500 text-sm font-medium">
                  Ver detalles →
                </button>
              </div>
            </div>

            {/* Idea Card 2 */}
            <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="h-3 w-3 bg-green-400 rounded-full mr-2"></div>
                    <span className="text-sm text-gray-500">Completada</span>
                  </div>
                  <span className="text-xs text-gray-400">1 semana</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Plataforma de E-learning
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  Sistema de cursos online con gamificación y seguimiento de progreso para estudiantes.
                </p>
                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    Educación
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    Web
                  </span>
                </div>
                <button className="text-blue-600 hover:text-blue-500 text-sm font-medium">
                  Ver detalles →
                </button>
              </div>
            </div>

            {/* Idea Card 3 */}
            <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="h-3 w-3 bg-gray-400 rounded-full mr-2"></div>
                    <span className="text-sm text-gray-500">Borrador</span>
                  </div>
                  <span className="text-xs text-gray-400">2 semanas</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Red Social para Desarrolladores
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  Plataforma donde desarrolladores pueden compartir código, colaborar en proyectos y hacer networking.
                </p>
                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                    Social
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    Desarrollo
                  </span>
                </div>
                <button className="text-blue-600 hover:text-blue-500 text-sm font-medium">
                  Ver detalles →
                </button>
              </div>
            </div>
          </div>

          {/* Add New Idea Button */}
          <div className="mt-8">
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium">
              + Nueva Idea
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}