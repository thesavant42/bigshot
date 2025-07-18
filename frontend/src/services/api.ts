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
  ApiKeyCollection
} from '../types';
import type { ChatContext } from './chatService';

interface GlobalWithEnv {
  process?: {
    env?: {
      REACT_APP_API_URL?: string;
    };
  };
}

const globalWithEnv = globalThis as unknown as GlobalWithEnv;

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: globalWithEnv.process?.env?.REACT_APP_API_URL || 'http://localhost:5000/api/v1',
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
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(username: string, password: string): Promise<{ token: string }> {
    const response = await this.api.post('/auth/login', { username, password });
    return response.data;
  }

  async verifyToken(): Promise<boolean> {
    try {
      await this.api.get('/auth/verify');
      return true;
    } catch {
      return false;
    }
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
  async sendMessage(message: string, context?: ChatContext): Promise<ChatMessage> {
    const response = await this.api.post('/chat/messages', {
      message,
      context,
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