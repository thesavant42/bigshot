import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './contexts/ThemeContext';
import { KeyboardProvider } from './contexts/KeyboardContext';
import MainLayout from './components/layout/MainLayout';
import DomainDashboard from './components/domain/DomainDashboard';
import KeyboardShortcutsHelp from './components/KeyboardShortcutsHelp';
import LoadingSpinner from './components/LoadingSpinner';
import PostAuthProof from './components/auth/PostAuthProof';
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
      // Go directly to dashboard - no more forced health check
      onLoginSuccess();
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50 dark:bg-dark-950 px-4 py-12">
      <div className="max-w-md w-full space-y-8">
        <div className="bg-white dark:bg-dark-800 rounded-2xl p-8 shadow-medium border border-neutral-200 dark:border-dark-700">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-neutral-900 dark:text-white tracking-tight">BigShot</h1>
            <p className="text-neutral-600 dark:text-neutral-400 mt-2 text-sm">Domain Reconnaissance Platform</p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div>
                <label 
                  htmlFor="username"
                  className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2"
                >
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={credentials.username}
                  onChange={(e) => setCredentials(prev => ({ ...prev, username: e.target.value }))}
                  className="w-full px-4 py-3 bg-white dark:bg-dark-700 border border-neutral-300 dark:border-dark-600 text-neutral-900 dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors"
                  required
                  autoComplete="username"
                  placeholder="Enter your username"
                />
              </div>
              
              <div>
                <label 
                  htmlFor="password"
                  className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2"
                >
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={credentials.password}
                  onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
                  className="w-full px-4 py-3 bg-white dark:bg-dark-700 border border-neutral-300 dark:border-dark-600 text-neutral-900 dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors"
                  required
                  autoComplete="current-password"
                  placeholder="Enter your password"
                />
              </div>
            </div>
            
            <button
              type="submit"
              disabled={login.isPending}
              className="w-full py-3 px-4 bg-accent-600 text-white rounded-xl hover:bg-accent-700 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-dark-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium"
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
              <div className="text-error-600 dark:text-error-400 text-sm text-center bg-error-50 dark:bg-error-900/20 p-3 rounded-xl border border-error-200 dark:border-error-800">
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

  // Only show post-auth proof if explicitly requested via URL parameter or if there are connectivity issues
  React.useEffect(() => {
    if (isAuthenticated && !showPostAuthProof) {
      const urlParams = new URLSearchParams(window.location.search);
      const showHealthCheck = urlParams.get('health') === 'true';
      
      if (showHealthCheck) {
        setShowPostAuthProof(true);
        // Clean up URL parameter
        window.history.replaceState({}, '', window.location.pathname);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- Only check on auth change
  }, [isAuthenticated]);

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

  if (showPostAuthProof) {
    return <PostAuthProof onContinue={() => setShowPostAuthProof(false)} />;
  }

  return (
    <MainLayout>
      <DomainDashboard />
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
