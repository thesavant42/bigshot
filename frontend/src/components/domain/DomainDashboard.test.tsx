import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DomainDashboard from './DomainDashboard';

// Mock the API hooks
jest.mock('../../hooks/useApi', () => ({
  useDomains: () => ({
    domains: { data: [] },
    isLoading: false,
    error: null,
    enumerateDomains: { mutateAsync: jest.fn() },
    bulkOperation: { mutateAsync: jest.fn() },
    refetch: jest.fn(),
  }),
  useJobs: () => ({
    jobs: [],
    isLoading: false,
  }),
}));

jest.mock('../../hooks/useWebSocket', () => ({
  useDomainUpdates: () => [],
}));

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

describe('DomainDashboard', () => {
  it('renders domain dashboard with search and controls', () => {
    const queryClient = createTestQueryClient();
    
    render(
      <QueryClientProvider client={queryClient}>
        <DomainDashboard />
      </QueryClientProvider>
    );

    expect(screen.getByPlaceholderText('Search domains...')).toBeInTheDocument();
    expect(screen.getByText('Filters')).toBeInTheDocument();
    expect(screen.getByText('Add Domain')).toBeInTheDocument();
    expect(screen.getByText('0 domains')).toBeInTheDocument();
  });

  it('shows no domains message when empty', () => {
    const queryClient = createTestQueryClient();
    
    render(
      <QueryClientProvider client={queryClient}>
        <DomainDashboard />
      </QueryClientProvider>
    );

    expect(screen.getByText('No domains found')).toBeInTheDocument();
  });
});