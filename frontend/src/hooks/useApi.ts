import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { webSocketService } from '../services/websocket';
import type { Domain, FilterOptions, TextCompletionRequest, EmbeddingsRequest, ChatMessage, BackendChatResponse } from '../types';
import type { ChatContext } from '../services/chatService';
/**
 * Simple UUID v4 generator (RFC4122 compliant, not cryptographically secure).
 * Use this for compatibility in all JS environments.
 */
function randomUUID() {
  // https://stackoverflow.com/a/2117523/2715716
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Additional types for API operations
interface BulkOperationData {
  tags?: string[];
  [key: string]: unknown;
}

interface EnumerationOptions {
  recursive?: boolean;
  max_depth?: number;
  timeout?: number;
  [key: string]: unknown;
}

export const useAuth = () => {
  const queryClient = useQueryClient();

  const login = useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      apiService.login(username, password),
    onSuccess: (data) => {
      localStorage.setItem('auth_token', data.token);
      queryClient.invalidateQueries({ queryKey: ['auth'] });
      // Refresh WebSocket connection with new auth token
      webSocketService.refreshConnection();
    },
  });

  const verifyToken = useQuery({
    queryKey: ['auth'],
    queryFn: () => apiService.verifyToken(),
    retry: false,
  });

  const logout = () => {
    localStorage.removeItem('auth_token');
    queryClient.clear();
    // Disconnect WebSocket on logout
    webSocketService.disconnect();
    window.location.href = '/login';
  };

  return {
    login,
    logout,
    isAuthenticated: verifyToken.data === true,
    isLoading: verifyToken.isLoading,
  };
};

export const useDomains = (filters: FilterOptions = {}) => {
  const queryClient = useQueryClient();

  const domains = useQuery({
    queryKey: ['domains', filters],
    queryFn: () => apiService.getDomains(filters),
    placeholderData: (previousData) => previousData,
  });

  const createDomain = useMutation({
    mutationFn: (domain: Partial<Domain>) => apiService.createDomain(domain),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] });
    },
  });

  const updateDomain = useMutation({
    mutationFn: ({ id, updates }: { id: number; updates: Partial<Domain> }) =>
      apiService.updateDomain(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] });
    },
  });

  const deleteDomain = useMutation({
    mutationFn: (id: number) => apiService.deleteDomain(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] });
    },
  });

  const bulkOperation = useMutation({
    mutationFn: ({ operation, domainIds, data }: { operation: string; domainIds: number[]; data?: BulkOperationData }) =>
      apiService.bulkDomainOperation(operation, domainIds, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] });
    },
  });

  const enumerateDomains = useMutation({
    mutationFn: ({ domains, sources, options }: { domains: string[]; sources?: string[]; options?: EnumerationOptions }) =>
      apiService.enumerateDomains(domains, sources, options),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    },
  });

  return {
    domains: domains.data,
    isLoading: domains.isLoading,
    error: domains.error,
    createDomain,
    updateDomain,
    deleteDomain,
    bulkOperation,
    enumerateDomains,
    refetch: domains.refetch,
  };
};

export const useDomainHierarchy = (rootDomain: string) => {
  return useQuery({
    queryKey: ['domain-hierarchy', rootDomain],
    queryFn: () => apiService.getDomainHierarchy(rootDomain),
    enabled: !!rootDomain,
  });
};

export const useJobs = () => {
  const queryClient = useQueryClient();

  const jobs = useQuery({
    queryKey: ['jobs'],
    queryFn: () => apiService.getJobs(),
    refetchInterval: 5000, // Refetch every 5 seconds
  });

  const cancelJob = useMutation({
    mutationFn: (id: string) => apiService.cancelJob(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    },
  });

  return {
    jobs: jobs.data,
    isLoading: jobs.isLoading,
    error: jobs.error,
    cancelJob,
    refetch: jobs.refetch,
  };
};

export const useJob = (id: string) => {
  return useQuery({
    queryKey: ['job', id],
    queryFn: () => apiService.getJob(id),
    enabled: !!id,
    refetchInterval: 2000, // Refetch every 2 seconds for active jobs
  });
};

export const useChat = () => {
  const queryClient = useQueryClient();

  const sendMessage = useMutation({
    mutationFn: ({ message, context }: { message: string; context?: ChatContext }) =>
      apiService.sendMessage(message, context),
    onMutate: async ({ message }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['conversation'] });

      // Snapshot the previous value
      const previousConversation = queryClient.getQueryData(['conversation']) as ChatMessage[];
      const safePreviousConversation = Array.isArray(previousConversation) ? previousConversation : [];

      // Optimistically add user message
      const userMessage: ChatMessage = {
        id: `user-${randomUUID()}`,
        content: message,
        role: 'user',
        timestamp: new Date().toISOString(),
      };

      queryClient.setQueryData(['conversation'], [...safePreviousConversation, userMessage]);

      // Return a context object with the snapshot
      return { previousConversation: safePreviousConversation };
    },
    onSuccess: (assistantResponse: BackendChatResponse) => {
      // Add assistant response to conversation
      const currentConversation = queryClient.getQueryData(['conversation']) as ChatMessage[] || [];
      
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        content: assistantResponse.content,
        role: 'assistant',
        timestamp: new Date().toISOString(),
      };

      queryClient.setQueryData(['conversation'], [...currentConversation, assistantMessage]);
    },
    onError: (_err) => {
      // On error, rollback to the snapshot
      if (context?.previousConversation) {
        queryClient.setQueryData(['conversation'], context.previousConversation);
      }
    },
  });

  const getConversation = useQuery({
    queryKey: ['conversation'],
    queryFn: () => apiService.getConversation('default'),
    refetchInterval: 30000, // Fixed: Reduced from 5 seconds to 30 seconds to prevent excessive re-renders
    refetchOnWindowFocus: false, // Fixed: Prevent refetch on window focus
    initialData: [], // Start with empty conversation
  });

  return {
    sendMessage,
    conversation: getConversation.data,
    isLoading: getConversation.isLoading,
    error: getConversation.error,
  };
};

// New LLM-specific hooks
export const useLLMProviders = () => {
  const queryClient = useQueryClient();

  const providers = useQuery({
    queryKey: ['llm-providers'],
    queryFn: () => apiService.getLLMProviders(),
  });

  const activeProvider = useQuery({
    queryKey: ['llm-providers', 'active'],
    queryFn: () => apiService.getActiveLLMProvider(),
  });

  const activateProvider = useMutation({
    mutationFn: (id: number) => apiService.activateLLMProvider(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['llm-providers'] });
    },
  });

  return {
    providers: providers.data,
    activeProvider: activeProvider.data,
    isLoading: providers.isLoading || activeProvider.isLoading,
    activateProvider,
  };
};

export const useAvailableModels = (enabled: boolean = true) => {
  return useQuery({
    queryKey: ['available-models'],
    queryFn: () => apiService.getAvailableModels(true),
    enabled,
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useTextCompletion = () => {
  return useMutation({
    mutationFn: (data: TextCompletionRequest) => apiService.createTextCompletion(data),
  });
};

export const useEmbeddings = () => {
  return useMutation({
    mutationFn: (data: EmbeddingsRequest) => apiService.createEmbeddings(data),
  });
};