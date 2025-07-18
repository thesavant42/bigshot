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
      // Set flag to show post-auth proof
      sessionStorage.setItem('just_logged_in', 'true');
      onLoginSuccess();
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-dark-950">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white dark:bg-dark-800 rounded-xl p-8 shadow-medium">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">BigShot</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">Domain Reconnaissance Platform</p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label 
                htmlFor="username"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Username
              </label>
              <input
                id="username"
                type="text"
                value={credentials.username}
                onChange={(e) => setCredentials(prev => ({ ...prev, username: e.target.value }))}
                className="w-full px-4 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                required
                autoComplete="username"
              />
            </div>
            
            <div>
              <label 
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
                className="w-full px-4 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                required
                autoComplete="current-password"
              />
            </div>
            
            <button
              type="submit"
              disabled={login.isPending}
              className="w-full py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
            
            {login.error && (
              <div className="text-error-600 dark:text-error-400 text-sm text-center bg-error-50 dark:bg-error-900/20 p-3 rounded-lg">
                Login failed. Please check your credentials.
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};

const AppContent: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const [showPostAuthProof, setShowPostAuthProof] = React.useState(false);

  // Show post-auth proof page after successful login
  React.useEffect(() => {
    if (isAuthenticated && !showPostAuthProof) {
      // Check if we just logged in by looking for a flag in sessionStorage
      const justLoggedIn = sessionStorage.getItem('just_logged_in');
      if (justLoggedIn) {
        setShowPostAuthProof(true);
        sessionStorage.removeItem('just_logged_in');
      }
    }
  }, [isAuthenticated, showPostAuthProof]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-dark-950">
        <LoadingSpinner size="lg" message="Loading application..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginScreen onLoginSuccess={() => setShowPostAuthProof(true)} />;
  }

  if (showPostAuthProof) {
    return <PostAuthProof onContinue={() => setShowPostAuthProof(false)} />;
  }

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
