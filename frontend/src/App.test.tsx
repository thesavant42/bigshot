import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';

// Mock the API hooks to avoid network calls during tests
jest.mock('./hooks/useApi', () => ({
  useAuth: () => ({
    isAuthenticated: false,
    isLoading: false,
    login: { mutateAsync: jest.fn(), isPending: false, error: null },
  }),
}));

// Mock WebSocket hook
jest.mock('./hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    isConnected: false,
    subscribe: jest.fn(),
    sendMessage: jest.fn(),
  }),
}));

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

describe('App', () => {
  it('renders login screen when not authenticated', () => {
    const queryClient = createTestQueryClient();
    
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    );

    expect(screen.getByText('BigShot')).toBeInTheDocument();
    expect(screen.getByText('Domain Reconnaissance Platform')).toBeInTheDocument();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
  });
});