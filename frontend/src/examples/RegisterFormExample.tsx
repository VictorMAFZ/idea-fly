/**
 * Example usage of RegisterForm component
 * This file demonstrates how to use the RegisterForm component
 */

import React from 'react';
import { RegisterForm } from '../components/auth/RegisterForm';
import { AuthStatus, RegisterRequest } from '../types/auth';

const RegisterFormExample: React.FC = () => {
  const handleRegister = async (data: RegisterRequest) => {
    console.log('Registration data:', data);
    // In real implementation, this would call the auth service
    await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
  };

  const handleSwitchToLogin = () => {
    console.log('Switch to login clicked');
    // In real implementation, this would navigate to login page
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <RegisterForm
          onSubmit={handleRegister}
          authStatus={AuthStatus.IDLE}
          onSwitchToLogin={handleSwitchToLogin}
          className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10"
        />
      </div>
    </div>
  );
};

export default RegisterFormExample;