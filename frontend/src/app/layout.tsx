import type { Metadata } from 'next';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { AuthProvider } from '../contexts/AuthContext';
import '../styles/globals.css';

export const metadata: Metadata = {
  title: 'IdeaFly - Autenticación',
  description: 'Accede a tu cuenta en IdeaFly para gestionar tus ideas',
  keywords: ['login', 'registro', 'cuenta', 'usuario', 'autenticación', 'ideas', 'google'],
  authors: [{ name: 'IdeaFly Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Get Google Client ID from environment variables
  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
  
  if (!googleClientId) {
    console.warn('NEXT_PUBLIC_GOOGLE_CLIENT_ID is not set. Google OAuth will not be available.');
  }

  return (
    <html lang="es">
      <body className="min-h-screen bg-gray-50">
        {googleClientId ? (
          <GoogleOAuthProvider clientId={googleClientId}>
            <AuthProvider>
              {children}
            </AuthProvider>
          </GoogleOAuthProvider>
        ) : (
          <AuthProvider>
            {children}
          </AuthProvider>
        )}
      </body>
    </html>
  );
}