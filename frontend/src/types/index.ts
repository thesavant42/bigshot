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