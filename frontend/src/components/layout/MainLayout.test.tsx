import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '../../contexts/ThemeContext';
import { KeyboardProvider } from '../../contexts/KeyboardContext';
import MainLayout from './MainLayout';

// Mock the hooks
vi.mock('../../hooks/useWebSocket', () => ({
  useWebSocket: () => ({ isConnected: true })
}));

vi.mock('../../hooks/useKeyboard', () => ({
  useKeyboard: () => ({ addShortcut: vi.fn() })
}));

// Mock the child components
vi.mock('../chat/ChatInterface', () => ({
  default: () => <div data-testid="chat-interface">Chat Interface</div>
}));

vi.mock('../monitoring/SystemMonitoringDashboard', () => ({
  default: () => <div data-testid="system-monitoring">System Monitoring</div>
}));

vi.mock('../auth/PostAuthProof', () => ({
  default: ({ onContinue }: { onContinue: () => void }) => (
    <div data-testid="post-auth-proof">
      <button onClick={onContinue}>Continue</button>
    </div>
  )
}));

vi.mock('../monitoring/ConfigurationManagement', () => ({
  default: () => <div data-testid="configuration-management">Configuration</div>
}));

const renderWithProviders = (children: React.ReactNode) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <KeyboardProvider>
          {children}
        </KeyboardProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe('MainLayout', () => {
  it('renders dashboard view by default', () => {
    renderWithProviders(
      <MainLayout>
        <div data-testid="dashboard-content">Dashboard Content</div>
      </MainLayout>
    );
    
    expect(screen.getByTestId('dashboard-content')).toBeInTheDocument();
    expect(screen.getByTestId('chat-interface')).toBeInTheDocument();
    expect(screen.getByText('AI Assistant')).toBeInTheDocument();
    expect(screen.getByText('Domain Reconnaissance')).toBeInTheDocument();
  });

  it('shows back button when not on dashboard', () => {
    renderWithProviders(
      <MainLayout>
        <div data-testid="dashboard-content">Dashboard Content</div>
      </MainLayout>
    );
    
    // Click on System Metrics to navigate away from dashboard
    fireEvent.click(screen.getByText('System Metrics'));
    
    // Should show back button and system monitoring content
    expect(screen.getByText('Back to Dashboard')).toBeInTheDocument();
    expect(screen.getByTestId('system-monitoring')).toBeInTheDocument();
  });

  it('navigates back to dashboard when back button is clicked', () => {
    renderWithProviders(
      <MainLayout>
        <div data-testid="dashboard-content">Dashboard Content</div>
      </MainLayout>
    );
    
    // Navigate to System Metrics
    fireEvent.click(screen.getByText('System Metrics'));
    expect(screen.getByText('Back to Dashboard')).toBeInTheDocument();
    
    // Click back button
    fireEvent.click(screen.getByText('Back to Dashboard'));
    
    // Should be back on dashboard
    expect(screen.queryByText('Back to Dashboard')).not.toBeInTheDocument();
    expect(screen.getByTestId('dashboard-content')).toBeInTheDocument();
  });

  it('shows different views when navigation items are clicked', () => {
    renderWithProviders(
      <MainLayout>
        <div data-testid="dashboard-content">Dashboard Content</div>
      </MainLayout>
    );
    
    // Test Service Health view
    fireEvent.click(screen.getByText('Service Health'));
    expect(screen.getByTestId('post-auth-proof')).toBeInTheDocument();
    
    // Test Settings view
    fireEvent.click(screen.getByText('Settings'));
    expect(screen.getByTestId('configuration-management')).toBeInTheDocument();
  });

  it('shows the main navigation elements', () => {
    renderWithProviders(
      <MainLayout>
        <div data-testid="dashboard-content">Dashboard Content</div>
      </MainLayout>
    );
    
    // Check that key navigation elements are present
    expect(screen.getByText('BigShot')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('AI Assistant')).toBeInTheDocument();
    expect(screen.getByText('Domain Reconnaissance')).toBeInTheDocument();
  });
});