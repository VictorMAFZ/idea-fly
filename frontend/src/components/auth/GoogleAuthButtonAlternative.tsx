'use client';

import { useState, useEffect } from 'react';

interface GoogleAuthButtonAlternativeProps {
  onSuccess: (token: string) => void;
  onError: (error: string) => void;
  disabled?: boolean;
}

declare global {
  interface Window {
    google?: any;
  }
}

export default function GoogleAuthButtonAlternative({
  onSuccess,
  onError,
  disabled = false
}: GoogleAuthButtonAlternativeProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoaded, setIsGoogleLoaded] = useState(false);

  useEffect(() => {
    // Load Google Identity Services
    const loadGoogleScript = () => {
      if (window.google) {
        setIsGoogleLoaded(true);
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = () => {
        if (window.google) {
          setIsGoogleLoaded(true);
        }
      };
      document.head.appendChild(script);
    };

    loadGoogleScript();
  }, []);

  const handleGoogleSignIn = async () => {
    if (!window.google || !isGoogleLoaded) {
      onError('Google Services no disponible');
      return;
    }

    try {
      setIsLoading(true);
      
      const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
      if (!clientId) {
        throw new Error('Google Client ID no configurado');
      }

      // Initialize Google OAuth
      window.google.accounts.oauth2.initTokenClient({
        client_id: clientId,
        scope: 'openid email profile',
        callback: async (response: any) => {
          try {
            if (response.error) {
              throw new Error(response.error);
            }

            console.log('Google Token Response:', response);
            
            if (response.access_token) {
              // Use the original endpoint with access token
              const backendResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/google`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ access_token: response.access_token }),
              });

              if (!backendResponse.ok) {
                const errorData = await backendResponse.json();
                throw new Error(errorData.detail?.message || 'Authentication failed');
              }

              const authData = await backendResponse.json();
              onSuccess(authData.access_token);
            } else {
              throw new Error('No access token received');
            }
          } catch (error) {
            console.error('OAuth processing error:', error);
            const errorMessage = error instanceof Error ? error.message : 'Authentication failed';
            onError(errorMessage);
          } finally {
            setIsLoading(false);
          }
        },
        error_callback: (error: any) => {
          console.error('Google OAuth Error:', error);
          onError('Google authentication failed');
          setIsLoading(false);
        }
      }).requestAccessToken();

    } catch (error) {
      console.error('Google Sign-In Error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Google authentication failed';
      onError(errorMessage);
      setIsLoading(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleGoogleSignIn}
      disabled={disabled || isLoading || !isGoogleLoaded}
      className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {isLoading ? (
        <>
          <div className="animate-spin -ml-1 mr-3 h-4 w-4 border-2 border-gray-300 border-t-gray-600 rounded-full"></div>
          Autenticando...
        </>
      ) : (
        <>
          <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          Continuar con Google
        </>
      )}
    </button>
  );
}