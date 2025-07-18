import type { ContextData } from '../types';
import type { ChatContext } from '../services/chatService';

/**
 * Converts ContextData from the API to ChatContext format used by the chat interface
 */
export function convertContextDataToChatContext(contextData: ContextData): ChatContext {
  return {
    current_domains: contextData.recent_domains?.map(d => d.root_domain),
    active_jobs: contextData.active_jobs?.map(j => j.id),
    timestamp: contextData.timestamp
  };
}