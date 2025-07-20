/// <reference types="vite/client" />

import { io, Socket } from 'socket.io-client';
import type { 
  WebSocketMessage, 
  JobUpdateData, 
  DomainDiscoveredData, 
  ChatMessageData 
} from '../types';

// Get WebSocket URL based on environment
// Uses the same smart environment detection as API configuration
const getWebSocketUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  
  // In development mode (vite dev server), always use current origin
  // This allows vite's proxy configuration to handle websocket routing
  // regardless of whether backend is on localhost or in Docker
  if (import.meta.env.DEV) {
    return window.location.origin; // Let vite proxy handle /socket.io -> backend
  }
  
  // For production and Docker environments, use current origin
  // nginx will proxy these to the appropriate backend service
  if (envUrl === "") {
    return window.location.origin; // Production/Docker: use current origin, nginx will proxy
  }
  
  // Fallback for explicit URL override (rare cases)
  return envUrl || 'http://localhost:5000';
};

export class WebSocketService {
  private socket: Socket | null = null;
  private eventHandlers: Map<string, Set<(data: unknown) => void>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second

  connect(url?: string): void {
    if (this.socket?.connected) return;

    const wsUrl = url || getWebSocketUrl();
    const token = localStorage.getItem('auth_token');
    
    this.socket = io(wsUrl, {
      transports: ['websocket'],
      auth: {
        token,
      },
      timeout: 10000, // 10 second timeout
      forceNew: true, // Force new connection
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0; // Reset on successful connection
    });

    this.socket.on('disconnect', (reason: string) => {
      console.log('WebSocket disconnected:', reason);
    });

    this.socket.on('connect_error', (error: Error) => {
      console.warn('WebSocket connection error:', error.message);
      this.handleReconnect();
    });

    this.socket.on('message', (message: WebSocketMessage) => {
      this.handleMessage(message);
    });

    // Handle specific event types
    this.socket.on('job_update', (data: JobUpdateData) => {
      this.emit('job_update', data);
    });

    this.socket.on('domain_discovered', (data: DomainDiscoveredData) => {
      this.emit('domain_discovered', data);
    });

    this.socket.on('chat_message', (data: ChatMessageData) => {
      this.emit('chat_message', data);
    });
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max WebSocket reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
    
    console.log(`Attempting WebSocket reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      if (!this.socket?.connected) {
        this.disconnect();
        this.connect();
      }
    }, delay);
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    this.emit(message.type, message.data);
  }

  private emit(event: string, data: unknown): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  subscribe(event: string, handler: (data: unknown) => void): () => void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    
    const handlers = this.eventHandlers.get(event)!;
    handlers.add(handler);

    // Return unsubscribe function
    return () => {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.eventHandlers.delete(event);
      }
    };
  }

  sendMessage(type: string, data: unknown): void {
    if (this.socket?.connected) {
      this.socket.emit('message', { type, data });
    }
  }

  joinRoom(room: string): void {
    if (this.socket?.connected) {
      this.socket.emit('join_room', room);
    }
  }

  leaveRoom(room: string): void {
    if (this.socket?.connected) {
      this.socket.emit('leave_room', room);
    }
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

export const webSocketService = new WebSocketService();
export default webSocketService;