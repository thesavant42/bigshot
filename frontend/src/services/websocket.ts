/// <reference types="vite/client" />

import { io, Socket } from 'socket.io-client';
import type { 
  WebSocketMessage, 
  JobUpdateData, 
  DomainDiscoveredData, 
  ChatMessageData 
} from '../types';

// Get WebSocket URL based on environment
const getWebSocketUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl === "") {
    return window.location.origin; // Production: use current origin, nginx will proxy
  }
  return envUrl || 'http://localhost:5000'; // Development
};

export class WebSocketService {
  private socket: Socket | null = null;
  private eventHandlers: Map<string, Set<(data: unknown) => void>> = new Map();

  connect(url?: string): void {
    if (this.socket?.connected) return;

    const wsUrl = url || getWebSocketUrl();
    const token = localStorage.getItem('auth_token');
    
    this.socket = io(wsUrl, {
      transports: ['websocket'],
      auth: {
        token,
      },
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
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