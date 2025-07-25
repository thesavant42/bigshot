// Domain types
export interface Domain {
  id: number;
  root_domain: string;
  subdomain: string;
  source: string;
  tags: string[];
  cdx_indexed: boolean;
  fetched_at: string;
}

// Job types
export interface Job {
  id: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  target_domains: string[];
  sources: string[];
  created_at: string;
  completed_at?: string;
  results_count?: number;
  progress?: number;
  error?: string;
}

// Chat types
export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  context?: {
    domains?: string[];
    jobs?: string[];
  };
}

// API Response types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface PaginatedResponse<T = unknown> {
  data: T[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

// UI types
export interface TreeNode {
  id: string;
  label: string;
  children: TreeNode[];
  data?: Domain;
  isExpanded?: boolean;
  level: number;
}

export interface FilterOptions {
  search?: string;
  root_domain?: string;
  source?: string;
  tags?: string[];
  page?: number;
  per_page?: number;
}

// WebSocket types
export interface WebSocketMessage {
  type: string;
  data: unknown;
  timestamp: string;
}

// Auth types
export interface AuthState {
  isAuthenticated: boolean;
  token?: string;
  user?: {
    id: string;
    username: string;
  };
}

// Additional API types
export interface BulkOperationData {
  [key: string]: unknown;
}

export interface EnumerationOptions {
  timeout?: number;
  max_results?: number;
  include_wildcards?: boolean;
  [key: string]: unknown;
}

export interface DomainHierarchy {
  root: string;
  subdomains: string[];
  relationships: Record<string, string[]>;
}

export interface AppSettings {
  [key: string]: string | number | boolean;
}

export interface ApiKeyCollection {
  [service: string]: string;
}

// Chat service specific types
export interface FunctionCall {
  name: string;
  arguments: Record<string, unknown>;
  result?: unknown;
}

export interface MCPToolParameters {
  type: string;
  properties: Record<string, unknown>;
  required?: string[];
}

// Backend chat response structure 
export interface BackendChatResponse {
  content: string;
  role: 'user' | 'assistant';
  function_calls?: FunctionCall[];
  usage?: {
    completion_tokens: number;
    completion_tokens_details?: unknown;
    prompt_tokens: number;
    prompt_tokens_details?: unknown;
    total_tokens: number;
  };
}

export interface ContextData {
  recent_domains?: Domain[];
  active_jobs?: Job[];
  recent_urls: string[];
  timestamp: string;
}

export interface StreamingChatChunk {
  type: 'content' | 'function_call' | 'error' | 'completion';
  content?: string;
  function_call?: FunctionCall;
  error?: string;
}

// WebSocket event data types
export interface JobUpdateData {
  job_id: string;
  status: Job['status'];
  progress?: number;
  results_count?: number;
  error?: string;
}

export interface DomainDiscoveredData {
  domain: Domain;
  source: string;
  job_id?: string;
}

export interface ChatMessageData {
  message: ChatMessage;
  session_id: string;
}

// Connectivity proof types for backend health check
export interface ServiceStatus {
  status: 'HEALTHY' | 'DEGRADED' | 'FAILED';
  message: string;
  connection_url?: string;
  active_workers?: number;
  broker_url?: string;
}

export interface ConnectivityProofResponse {
  authentication: {
    status: 'SUCCESS';
    user: string;
    timestamp: string;
    message: string;
  };
  backend_services: {
    database: ServiceStatus;
    redis: ServiceStatus;
    celery: ServiceStatus;
  };
  environment: {
    service_name: string;
    hostname: string;
    flask_env: string;
    container_id: string;
  };
  client: {
    ip_address: string;
    user_agent: string;
    request_timestamp: string;
  };
  overall_status: {
    healthy_services: number;
    total_services: number;
    status: 'HEALTHY' | 'DEGRADED';
  };
}

// LLM Provider types
export interface LLMProviderConfig {
  id: number;
  provider: 'openai' | 'lmstudio' | 'custom';
  name: string;
  base_url: string;
  api_key_masked?: string;
  model: string;
  is_active: boolean;
  is_default: boolean;
  connection_timeout: number;
  max_tokens: number;
  temperature: number;
  created_at: string;
  updated_at: string;
}

export interface LLMProviderConfigInput {
  provider: 'openai' | 'lmstudio' | 'custom';
  name: string;
  base_url: string;
  api_key?: string;
  model: string;
  is_default?: boolean;
  connection_timeout?: number;
  max_tokens?: number;
  temperature?: number;
}

export interface LLMProviderTestResult {
  success: boolean;
  response_time?: number;
  models_available?: string[];
  test_response?: string;
  error?: string;
  provider_info: {
    name: string;
    provider: string;
    base_url: string;
    model: string;
  };
  timestamp: string;
}

export interface LLMProviderAuditLog {
  id: number;
  provider_config_id?: number;
  action: 'created' | 'updated' | 'activated' | 'tested' | 'deleted';
  old_values?: Record<string, unknown>;
  new_values?: Record<string, unknown>;
  test_result?: LLMProviderTestResult;
  user_id?: number;
  created_at: string;
}

export interface LLMProviderPreset {
  provider: 'openai' | 'lmstudio' | 'custom';
  name: string;
  base_url: string;
  model: string;
  requires_api_key: boolean;
  description: string;
}

// LM Studio Model types
export interface LMStudioModel {
  id: string;
  object: string;
  type?: 'llm' | 'vlm' | 'embeddings';
  arch?: string;
  state?: 'loaded' | 'not-loaded';
  max_context_length?: number;
  displayName?: string;
  created?: number;
  owned_by?: string;
  publisher?: string;
  compatibility_type?: string;
  quantization?: string;
}

export interface AvailableModelsResponse {
  models: string[] | LMStudioModel[];
  provider: {
    name: string;
    provider: string;
    base_url: string;
    model: string;
    source: string;
  };
}

export interface TextCompletionRequest {
  prompt: string;
  model?: string;
  max_tokens?: number;
  temperature?: number;
  stream?: boolean;
  stop?: string | string[];
}

export interface EmbeddingsRequest {
  input: string | string[];
  model?: string;
}