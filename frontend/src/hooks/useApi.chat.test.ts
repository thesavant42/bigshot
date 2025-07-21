import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useChat } from './useApi';
import { apiService } from '../services/api';

// Mock the apiService
vi.mock('../services/api', () => ({
  apiService: {
    sendMessage: vi.fn(),
    getConversation: vi.fn(),
  },
}));

// Mock WebSocket service
vi.mock('../services/websocket', () => ({
  webSocketService: {
    refreshConnection: vi.fn(),
    disconnect: vi.fn(),
  },
}));

describe('useChat hook - Response Structure Handling', () => {
  let queryClient: QueryClient;
  
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
        mutations: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    React.createElement(QueryClientProvider, { client: queryClient }, children)
  );

  it('should handle backend response structure correctly', async () => {
    // Mock the backend response structure from the issue
    const mockBackendResponse = {
      content: "\n\nHello! How can I assist you with your cybersecurity reconnaissance or bug bounty research today? Let me know if you need help analyzing domains, checking URLs, managing jobs, or looking up information!",
      function_calls: [],
      role: "assistant",
      usage: {
        completion_tokens: 189,
        completion_tokens_details: null,
        prompt_tokens: 667,
        prompt_tokens_details: null,
        total_tokens: 856
      }
    };

    // Mock getConversation to return empty array initially
    vi.mocked(apiService.getConversation).mockResolvedValue([]);
    
    // Mock sendMessage to return the assistant response
    vi.mocked(apiService.sendMessage).mockResolvedValue(mockBackendResponse);

    const { result } = renderHook(() => useChat(), { wrapper });

    // Initially conversation should be empty
    await waitFor(() => {
      expect(result.current.conversation).toEqual([]);
    });

    // Send a message
    await result.current.sendMessage.mutateAsync({
      message: "hello there"
    });

    // Wait for the mutation to complete and check conversation state
    await waitFor(() => {
      const conversation = result.current.conversation;
      expect(conversation).toHaveLength(2); // User message + assistant response
      
      // Check user message
      expect(conversation[0]).toMatchObject({
        role: 'user',
        content: 'hello there'
      });
      expect(conversation[0].id).toMatch(/^user-\d+$/);
      expect(conversation[0].timestamp).toBeDefined();
      
      // Check assistant message - this is the key fix
      expect(conversation[1]).toMatchObject({
        role: 'assistant',
        content: mockBackendResponse.content // Should extract content from response
      });
      expect(conversation[1].id).toMatch(/^assistant-\d+$/);
      expect(conversation[1].timestamp).toBeDefined();
    });
  });

  it('should handle errors correctly and rollback optimistic updates', async () => {
    // Mock getConversation to return empty array
    vi.mocked(apiService.getConversation).mockResolvedValue([]);
    
    // Mock sendMessage to throw an error
    vi.mocked(apiService.sendMessage).mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useChat(), { wrapper });

    // Initially conversation should be empty
    await waitFor(() => {
      expect(result.current.conversation).toEqual([]);
    });

    // Send a message that will fail
    try {
      await result.current.sendMessage.mutateAsync({
        message: "hello there"
      });
    } catch (error) {
      // Expected to fail
    }

    // Wait for the mutation to complete and check that conversation was rolled back
    await waitFor(() => {
      // Conversation should be empty due to rollback
      expect(result.current.conversation).toEqual([]);
    });
  });

  it('should generate unique IDs for messages', async () => {
    // Mock responses
    vi.mocked(apiService.getConversation).mockResolvedValue([]);
    vi.mocked(apiService.sendMessage).mockResolvedValue({
      content: "Response 1",
      role: "assistant"
    });

    const { result } = renderHook(() => useChat(), { wrapper });

    // Send first message
    await result.current.sendMessage.mutateAsync({
      message: "message 1"
    });

    await waitFor(() => {
      expect(result.current.conversation).toHaveLength(2);
    });

    const firstConversation = result.current.conversation;

    // Send second message
    vi.mocked(apiService.sendMessage).mockResolvedValue({
      content: "Response 2", 
      role: "assistant"
    });

    await result.current.sendMessage.mutateAsync({
      message: "message 2"
    });

    await waitFor(() => {
      expect(result.current.conversation).toHaveLength(4);
    });

    const secondConversation = result.current.conversation;

    // Check that all IDs are unique
    const ids = secondConversation.map(msg => msg.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(4); // All IDs should be unique
  });
});