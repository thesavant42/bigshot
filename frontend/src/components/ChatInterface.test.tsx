import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ChatInterface from './ChatInterface'

// Mock websocket
vi.mock('../hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    socket: null,
    isConnected: false,
    sendMessage: vi.fn(),
    subscribeToEvent: vi.fn(),
    unsubscribeFromEvent: vi.fn(),
  }),
}))

describe('ChatInterface', () => {
  it('renders chat interface component', async () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })
    
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ChatInterface />
        </BrowserRouter>
      </QueryClientProvider>
    )
    
    // Test that the component renders without crashing
    expect(document.body).toBeInTheDocument()
  })
})