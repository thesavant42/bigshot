import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './contexts/ThemeContext';
import { KeyboardProvider } from './contexts/KeyboardContext';
import MainLayout from './components/layout/MainLayout';
import DomainDashboard from './components/domain/DomainDashboard';
import ChatInterface from './components/ChatInterface';
import SplitLayout from './components/SplitLayout';
import KeyboardShortcutsHelp from './components/KeyboardShortcutsHelp';
import LoadingSpinner from './components/LoadingSpinner';
import PostAuthProof from './components/auth/PostAuthProof';
import ErrorBoundary from './components/ErrorBoundary';
import { useAuth } from './hooks/useApi';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const LoginScreen: React.FC<{ onLoginSuccess: () => void }> = ({ onLoginSuccess }) => {
  const { login } = useAuth();
  const [credentials, setCredentials] = React.useState({
    username: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login.mutateAsync(credentials);
      // Remove the post-auth proof flag since we're skipping it
      onLoginSuccess();
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-100 dark:from-dark-900 dark:to-dark-950 px-4">
      <div className="max-w-md w-full">
        <div className="bg-white dark:bg-dark-800 rounded-3xl p-8 shadow-strong border border-gray-100 dark:border-gray-700">
          <div className="text-center mb-8">
            <div className="mx-auto w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center mb-4">
              <span className="text-2xl font-bold text-white">B</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">BigShot</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2 font-medium">Domain Reconnaissance Platform</p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-1">
              <label 
                htmlFor="username"
                className="block text-sm font-semibold text-gray-700 dark:text-gray-300"
              >
                Username
              </label>
              <input
                id="username"
                type="text"
                value={credentials.username}
                onChange={(e) => setCredentials(prev => ({ ...prev, username: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-dark-700 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 font-medium placeholder-gray-400 dark:placeholder-gray-500"
                required
                autoComplete="username"
                placeholder="Enter your username"
              />
            </div>
            
            <div className="space-y-1">
              <label 
                htmlFor="password"
                className="block text-sm font-semibold text-gray-700 dark:text-gray-300"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-dark-700 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 font-medium placeholder-gray-400 dark:placeholder-gray-500"
                required
                autoComplete="current-password"
                placeholder="Enter your password"
              />
            </div>
            
            <div className="pt-2">
              <button
                type="submit"
                disabled={login.isPending}
                className="w-full py-3.5 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-xl font-semibold text-base transition-all duration-200 transform hover:scale-[1.02] disabled:scale-100 shadow-medium hover:shadow-strong disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-dark-800"
              >
                {login.isPending ? (
                  <div className="flex items-center justify-center">
                    <LoadingSpinner size="sm" variant="white" />
                    <span className="ml-2">Signing in...</span>
                  </div>
                ) : (
                  'Sign In'
                )}
              </button>
            </div>
            
            {login.error && (
              <div className="text-error-600 dark:text-error-400 text-sm bg-error-50 dark:bg-error-900/20 p-4 rounded-xl border border-error-200 dark:border-error-800 font-medium">
                <div className="flex items-center">
                  <svg className="w-4 h-4 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  Login failed. Please check your credentials.
                </div>
              </div>
            )}
          </form>
          
          <div className="mt-8 pt-6 border-t border-gray-100 dark:border-gray-700">
            <p className="text-center text-sm text-gray-500 dark:text-gray-400">
              Secure access to domain reconnaissance tools
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

const AppContent: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-dark-950">
        <LoadingSpinner size="lg" message="Loading application..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginScreen onLoginSuccess={() => {}} />;
  }

  // Skip post-auth proof and go directly to main dashboard
  return (
    <MainLayout>
      <SplitLayout
        leftPanel={
          <ErrorBoundary
            onError={(error, errorInfo) => {
              // Log error for debugging
              console.error('ChatInterface Error:', error, errorInfo);
              // Could also send to error reporting service here
            }}
          >
            <ChatInterface />
          </ErrorBoundary>
        }
        rightPanel={<DomainDashboard />}
      />
    </MainLayout>
  );
};

function App() {
  return (
    <ThemeProvider>
      <KeyboardProvider>
        <QueryClientProvider client={queryClient}>
          <AppContent />
          <KeyboardShortcutsHelp />
        </QueryClientProvider>
      </KeyboardProvider>
    </ThemeProvider>
  );
}

export default App;
