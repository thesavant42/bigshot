/// <reference types="vite/client" />

import axios, { type AxiosInstance } from 'axios';
import type { 
  PaginatedResponse, 
  Domain, 
  Job, 
  ChatMessage, 
  FilterOptions, 
  BulkOperationData,
  EnumerationOptions,
  DomainHierarchy,
  AppSettings,
  ApiKeyCollection,
  ConnectivityProofResponse,
  ApiResponse,
  LLMProviderConfig,
  LLMProviderConfigInput,
  LLMProviderTestResult,
  LLMProviderAuditLog,
  LLMProviderPreset,
  AvailableModelsResponse,
  TextCompletionRequest,
  EmbeddingsRequest,
  BackendChatResponse
} from '../types';
import type { ChatContext } from './chatService';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    // Smart environment detection for API base URL configuration
    // Handles different deployment scenarios:
    // 1. Development on host (vite dev server) - use relative URLs for proxy
    // 2. Production in Docker - use relative URLs for nginx proxy  
    // 3. Development in Docker - use relative URLs for nginx proxy
    const getApiBaseUrl = () => {
      const envUrl = import.meta.env.VITE_API_URL;
      
      // In development mode (vite dev server), always use relative URLs
      // This allows vite's proxy configuration to handle backend routing
      // regardless of whether backend is on localhost or in Docker
      if (import.meta.env.DEV) {
        return "/api/v1"; // Let vite proxy handle /api -> backend
      }
      
      // For production and Docker environments, use relative URLs
      // nginx will proxy these to the appropriate backend service
      if (envUrl === "") {
        return "/api/v1"; // Production/Docker: use relative URLs, nginx will proxy
      }
      
      // Fallback for explicit URL override (rare cases)
      return (envUrl || 'http://localhost:5000') + '/api/v1';
    };

    this.api = axios.create({
      baseURL: getApiBaseUrl(),
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor to handle errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          // Don't reload the page, let React handle the state change
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(username: string, password: string): Promise<{ token: string }> {
    const response = await this.api.post('/auth/login', { username, password });
    return { token: response.data.data.access_token };
  }

  async verifyToken(): Promise<boolean> {
    try {
      await this.api.post('/auth/verify');
      return true;
    } catch {
      return false;
    }
  }

  async getConnectivityProof(): Promise<ApiResponse<ConnectivityProofResponse>> {
    const response = await this.api.get('/auth/connectivity-proof');
    return response.data;
  }

  // Domain endpoints
  async getDomains(filters: FilterOptions = {}): Promise<PaginatedResponse<Domain>> {
    const response = await this.api.get('/domains', { params: filters });
    return response.data;
  }

  async getDomain(id: number): Promise<Domain> {
    const response = await this.api.get(`/domains/${id}`);
    return response.data.data;
  }

  async createDomain(domain: Partial<Domain>): Promise<Domain> {
    const response = await this.api.post('/domains', domain);
    return response.data.data;
  }

  async updateDomain(id: number, updates: Partial<Domain>): Promise<Domain> {
    const response = await this.api.put(`/domains/${id}`, updates);
    return response.data.data;
  }

  async deleteDomain(id: number): Promise<void> {
    await this.api.delete(`/domains/${id}`);
  }

  async bulkDomainOperation(operation: string, domainIds: number[], data?: BulkOperationData): Promise<void> {
    await this.api.post('/domains/bulk', {
      operation,
      domain_ids: domainIds,
      ...data,
    });
  }

  async enumerateDomains(domains: string[], sources: string[] = ['crt.sh'], options: EnumerationOptions = {}): Promise<Job> {
    const response = await this.api.post('/domains/enumerate', {
      domains,
      sources,
      options,
    });
    return response.data.data;
  }

  async getDomainHierarchy(rootDomain: string): Promise<DomainHierarchy> {
    const response = await this.api.get(`/domains/hierarchy/${rootDomain}`);
    return response.data.data;
  }

  // Job endpoints
  async getJobs(): Promise<Job[]> {
    const response = await this.api.get('/jobs');
    return response.data.data;
  }

  async getJob(id: string): Promise<Job> {
    const response = await this.api.get(`/jobs/${id}`);
    return response.data.data;
  }

  async cancelJob(id: string): Promise<void> {
    await this.api.post(`/jobs/${id}/cancel`);
  }

  async getJobLogs(id: string): Promise<string[]> {
    const response = await this.api.get(`/jobs/${id}/logs`);
    return response.data.data;
  }

  // Chat endpoints
  async sendMessage(message: string, context?: ChatContext): Promise<BackendChatResponse> {
    // Get the current active model for the chat request
    let model: string | undefined;
    try {
      const activeProvider = await this.getActiveLLMProvider();
      model = activeProvider?.model;
    } catch (error) {
      console.warn('Could not get active provider model for chat request:', error);
      // Continue without model, let backend handle it
    }

    const response = await this.api.post('/chat/messages', {
      message,
      context,
      model, // Include model field if available
    });
    return response.data.data;
  }

  async getConversation(sessionId: string): Promise<ChatMessage[]> {
    const response = await this.api.get(`/chat/conversations/${sessionId}`);
    return response.data.data;
  }

  // Settings endpoints
  async getSettings(): Promise<AppSettings> {
    const response = await this.api.get('/settings/config');
    return response.data.data;
  }

  async updateSettings(settings: AppSettings): Promise<AppSettings> {
    const response = await this.api.put('/settings/config', settings);
    return response.data.data;
  }

  async getApiKeys(): Promise<ApiKeyCollection> {
    const response = await this.api.get('/settings/api-keys');
    return response.data.data;
  }

  async updateApiKey(service: string, key: string): Promise<void> {
    await this.api.put(`/settings/api-keys/${service}`, { key });
  }

  // LLM Provider endpoints
  async getLLMProviders(): Promise<LLMProviderConfig[]> {
    const response = await this.api.get('/llm-providers');
    return response.data.data;
  }

  async getActiveLLMProvider(): Promise<LLMProviderConfig> {
    const response = await this.api.get('/llm-providers/active');
    return response.data.data;
  }

  async createLLMProvider(provider: LLMProviderConfigInput): Promise<LLMProviderConfig> {
    const response = await this.api.post('/llm-providers', provider);
    return response.data.data;
  }

  async updateLLMProvider(id: number, updates: Partial<LLMProviderConfigInput>): Promise<LLMProviderConfig> {
    const response = await this.api.put(`/llm-providers/${id}`, updates);
    return response.data.data;
  }

  async deleteLLMProvider(id: number): Promise<void> {
    await this.api.delete(`/llm-providers/${id}`);
  }

  async activateLLMProvider(id: number): Promise<{ message: string; provider: LLMProviderConfig }> {
    const response = await this.api.post(`/llm-providers/${id}/activate`);
    return response.data.data;
  }

  async testLLMProvider(id: number): Promise<{ provider_id: number; test_result: LLMProviderTestResult }> {
    const response = await this.api.post(`/llm-providers/${id}/test`);
    return response.data.data;
  }

  async getLLMProviderAuditLogs(limit: number = 50): Promise<LLMProviderAuditLog[]> {
    const response = await this.api.get('/llm-providers/audit-logs', { params: { limit } });
    return response.data.data;
  }

  async getLLMProviderPresets(): Promise<LLMProviderPreset[]> {
    const response = await this.api.get('/llm-providers/presets');
    return response.data.data;
  }

  // New LM Studio specific endpoints
  async getAvailableModels(detailed: boolean = false): Promise<AvailableModelsResponse> {
    const response = await this.api.get('/llm-providers/models', { params: { detailed: detailed.toString() } });
    return response.data.data;
  }

  async createTextCompletion(data: TextCompletionRequest): Promise<object> {
    const response = await this.api.post('/llm-providers/completions', data);
    return response.data.data;
  }

  async createEmbeddings(data: EmbeddingsRequest): Promise<object> {
    const response = await this.api.post('/llm-providers/embeddings', data);
    return response.data.data;
  }

  // Health and monitoring endpoints
  async get<T = unknown>(path: string): Promise<T> {
    const response = await this.api.get(path);
    return response.data;
  }

  async put(path: string, data: unknown): Promise<unknown> {
    const response = await this.api.put(path, data);
    return response.data;
  }

  async post(path: string, data: unknown): Promise<unknown> {
    const response = await this.api.post(path, data);
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;