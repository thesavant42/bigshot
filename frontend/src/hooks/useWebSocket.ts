import { useEffect, useRef, useState } from 'react';
import { webSocketService } from '../services/websocket';

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const subscribersRef = useRef<Map<string, Set<(data: any) => void>>>(new Map());

  useEffect(() => {
    webSocketService.connect();
    
    const checkConnection = () => {
      setIsConnected(webSocketService.isConnected());
    };

    const interval = setInterval(checkConnection, 1000);
    checkConnection();

    return () => {
      clearInterval(interval);
      webSocketService.disconnect();
    };
  }, []);

  const subscribe = (event: string, handler: (data: any) => void) => {
    if (!subscribersRef.current.has(event)) {
      subscribersRef.current.set(event, new Set());
    }
    
    const subscribers = subscribersRef.current.get(event)!;
    subscribers.add(handler);

    const unsubscribe = webSocketService.subscribe(event, handler);

    return () => {
      unsubscribe();
      subscribers.delete(handler);
      if (subscribers.size === 0) {
        subscribersRef.current.delete(event);
      }
    };
  };

  const sendMessage = (type: string, data: any) => {
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
  const [jobUpdates, setJobUpdates] = useState<any[]>([]);

  useEffect(() => {
    const unsubscribe = subscribe('job_update', (data: any) => {
      setJobUpdates(prev => [...prev.slice(-49), data]); // Keep last 50 updates
    });

    return unsubscribe;
  }, [subscribe]);

  return jobUpdates;
};

export const useDomainUpdates = () => {
  const { subscribe } = useWebSocket();
  const [domainUpdates, setDomainUpdates] = useState<any[]>([]);

  useEffect(() => {
    const unsubscribe = subscribe('domain_discovered', (data: any) => {
      setDomainUpdates(prev => [...prev.slice(-99), data]); // Keep last 100 updates
    });

    return unsubscribe;
  }, [subscribe]);

  return domainUpdates;
};

export const useChatUpdates = () => {
  const { subscribe } = useWebSocket();
  const [chatUpdates, setChatUpdates] = useState<any[]>([]);

  useEffect(() => {
    const unsubscribe = subscribe('chat_message', (data: any) => {
      setChatUpdates(prev => [...prev.slice(-49), data]); // Keep last 50 messages
    });

    return unsubscribe;
  }, [subscribe]);

  return chatUpdates;
};