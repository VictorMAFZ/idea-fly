import type { Metadata } from 'next';
import { AuthProvider } from '../contexts/AuthContext';
import '../styles/globals.css';

export const metadata: Metadata = {
  title: 'IdeaFly - Registro',
  description: 'Crea tu cuenta en IdeaFly para comenzar a gestionar tus ideas',
  keywords: ['registro', 'cuenta', 'usuario', 'autenticación', 'ideas'],
  authors: [{ name: 'IdeaFly Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-gray-50">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}