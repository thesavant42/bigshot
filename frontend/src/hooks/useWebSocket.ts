import { useEffect, useRef, useState } from 'react';
import { webSocketService } from '../services/websocket';
import type { Job, Domain, ChatMessage } from '../types';

// WebSocket event data types
interface JobUpdateData extends Partial<Job> {
  id: string;
}

interface DomainUpdateData extends Partial<Domain> {
  id?: number;
}

// Generic WebSocket event handler
type WebSocketEventHandler<T = unknown> = (data: T) => void;

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const subscribersRef = useRef<Map<string, Set<(data: unknown) => void>>>(new Map());

  useEffect(() => {
    webSocketService.connect();
    
    const checkConnection = () => {
      setIsConnected(webSocketService.isConnected());
    };

    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds instead of 10
    checkConnection();

    return () => {
      clearInterval(interval);
      webSocketService.disconnect();
    };
  }, []);

  const subscribe = <T = unknown>(event: string, handler: WebSocketEventHandler<T>) => {
    if (!subscribersRef.current.has(event)) {
      subscribersRef.current.set(event, new Set());
    }
    
    const subscribers = subscribersRef.current.get(event)!;
    // Type-safe: WebSocketEventHandler<T> = (data: T) => void
    // is assignable to (data: unknown) => void since T extends unknown
    const unknownHandler = handler as (data: unknown) => void;
    subscribers.add(unknownHandler);

    const unsubscribe = webSocketService.subscribe(event, unknownHandler);

    return () => {
      unsubscribe();
      subscribers.delete(unknownHandler);
      if (subscribers.size === 0) {
        subscribersRef.current.delete(event);
      }
    };
  };

  const sendMessage = (type: string, data: unknown) => {
    webSocketService.sendMessage(type, data);
  };

  return {
    isConnected,
    subscribe,
    sendMessage,
  };
};

export const useJobUpdates = () => {
  const { subscribe } = useWebSocket();
  const [jobUpdates, setJobUpdates] = useState<JobUpdateData[]>([]);

  useEffect(() => {
    const unsubscribe = subscribe<JobUpdateData>('job_update', (data: JobUpdateData) => {
      setJobUpdates(prev => [...prev.slice(-49), data]); // Keep last 50 updates
    });

    return unsubscribe;
    // eslint-disable-next-line react-hooks/exhaustive-deps -- Intentionally omitting 'subscribe' to prevent infinite re-renders
  }, []); 

  return jobUpdates;
};

export const useDomainUpdates = () => {
  const { subscribe } = useWebSocket();
  const [domainUpdates, setDomainUpdates] = useState<DomainUpdateData[]>([]);

  useEffect(() => {
    const unsubscribe = subscribe<DomainUpdateData>('domain_discovered', (data: DomainUpdateData) => {
      setDomainUpdates(prev => [...prev.slice(-99), data]); // Keep last 100 updates
    });

    return unsubscribe;
    // eslint-disable-next-line react-hooks/exhaustive-deps -- Intentionally omitting 'subscribe' to prevent infinite re-renders
  }, []); 

  return domainUpdates;
};

export const useChatUpdates = () => {
  const { subscribe } = useWebSocket();
  const [chatUpdates, setChatUpdates] = useState<ChatMessage[]>([]);

  useEffect(() => {
    const unsubscribe = subscribe<ChatMessage>('chat_message', (data: ChatMessage) => {
      setChatUpdates(prev => [...prev.slice(-49), data]); // Keep last 50 messages
    });

    return unsubscribe;
    // eslint-disable-next-line react-hooks/exhaustive-deps -- Intentionally omitting 'subscribe' to prevent infinite re-renders
  }, []); 

  return chatUpdates;
};