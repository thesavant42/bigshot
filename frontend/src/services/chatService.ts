import axios from 'axios';
import { API_BASE_URL } from '../config';
import type { FunctionCall, MCPToolParameters, ContextData, StreamingChatChunk } from '../types';

export interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  function_calls?: FunctionCall[];
  created_at?: string;
}

export interface ChatResponse {
  content: string;
  role: string;
  function_calls?: FunctionCall[];
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface ChatContext {
  user_id?: string;
  current_domains?: string[];
  active_jobs?: string[];
  session_id?: string;
  timestamp?: string;
}

export interface Conversation {
  id: number;
  session_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface MCPTool {
  type: string;
  function: {
    name: string;
    description: string;
    parameters: MCPToolParameters;
  };
}

class ChatService {
  private baseURL = `${API_BASE_URL}/api/v1`;

  async sendMessage(
    message: string,
    conversationHistory: ChatMessage[] = [],
    context: ChatContext = {},
    stream: boolean = false
  ): Promise<ChatResponse | EventSource> {
    const token = localStorage.getItem('token');
    
    if (stream) {
      // Note: EventSource doesn't support custom headers, so we'll use fetch with SSE
      const eventSource = new EventSource(`${this.baseURL}/chat/messages?stream=true`);
      
      // Send the message via POST first
      await axios.post(
        `${this.baseURL}/chat/messages`,
        {
          message,
          conversation_history: conversationHistory,
          context,
          stream: true,
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      return eventSource;
    } else {
      const response = await axios.post(
        `${this.baseURL}/chat/messages`,
        {
          message,
          conversation_history: conversationHistory,
          context,
          stream: false,
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      return response.data.data;
    }
  }

  async getModels(): Promise<string[]> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${this.baseURL}/chat/models`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return response.data.data.models;
  }

  async getStatus(): Promise<{
    available: boolean;
    models: string[];
    timestamp: string;
  }> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${this.baseURL}/chat/status`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return response.data.data;
  }

  async getContext(): Promise<ContextData> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${this.baseURL}/chat/context`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return response.data.data;
  }

  async getConversations(): Promise<Conversation[]> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${this.baseURL}/chat/conversations`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return response.data.data.conversations;
  }

  async getConversation(sessionId: string): Promise<{
    session_id: string;
    messages: ChatMessage[];
    created_at: string;
  }> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${this.baseURL}/chat/conversations/${sessionId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return response.data.data;
  }

  async getMCPTools(): Promise<MCPTool[]> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${this.baseURL}/mcp/tools`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return response.data.data.tools;
  }

  async executeMCPTool(toolName: string, args: Record<string, unknown>): Promise<unknown> {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${this.baseURL}/mcp/execute`,
      {
        tool_name: toolName,
        arguments: args,
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    
    return response.data.data;
  }

  // Helper method to create a streaming chat
  async createStreamingChat(
    message: string,
    conversationHistory: ChatMessage[] = [],
    context: ChatContext = {},
    onChunk: (chunk: StreamingChatChunk) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ): Promise<void> {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${this.baseURL}/chat/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversation_history: conversationHistory,
          context,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No readable stream available');
      }

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          onComplete();
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              if (data.type === 'error') {
                onError(new Error(data.error));
                return;
              } else if (data.type === 'completion') {
                onComplete();
                return;
              } else {
                onChunk(data);
              }
            } catch {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (e) {
      // Handle unknown error types safely by checking instance before passing to onError
      if (e instanceof Error) {
        onError(e);
      } else {
        onError(new Error(String(e)));
      }
    }
  }
}

export const chatService = new ChatService();