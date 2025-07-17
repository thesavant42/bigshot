import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';
import type { Domain, FilterOptions } from '../types';

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

interface ChatContext {
  domains?: string[];
  jobs?: string[];
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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversation'] });
    },
  });

  const getConversation = useQuery({
    queryKey: ['conversation'],
    queryFn: () => apiService.getConversation('default'),
    refetchInterval: 5000, // Refetch every 5 seconds
  });

  return {
    sendMessage,
    conversation: getConversation.data,
    isLoading: getConversation.isLoading,
    error: getConversation.error,
  };
};