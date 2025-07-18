import { describe, it, expect } from 'vitest';
import { convertContextDataToChatContext } from '../utils/contextConversion';
import type { ContextData, Domain, Job } from '../types';
import type { ChatContext } from '../services/chatService';

describe('ChatInterface context conversion', () => {
  it('should convert full context data correctly', () => {
    const mockDomains: Domain[] = [
      {
        id: 1,
        root_domain: 'example.com',
        subdomain: 'www.example.com',
        source: 'manual',
        tags: [],
        cdx_indexed: false,
        fetched_at: '2024-01-01T10:00:00Z'
      },
      {
        id: 2,
        root_domain: 'test.com',
        subdomain: 'api.test.com',
        source: 'auto',
        tags: ['api'],
        cdx_indexed: true,
        fetched_at: '2024-01-01T11:00:00Z'
      }
    ];

    const mockJobs: Job[] = [
      {
        id: 'job1',
        type: 'subdomain',
        status: 'running',
        target_domains: ['example.com'],
        sources: ['crt.sh'],
        created_at: '2024-01-01T09:00:00Z',
        progress: 50
      },
      {
        id: 'job2',
        type: 'enumeration',
        status: 'completed',
        target_domains: ['test.com'],
        sources: ['dnsdumpster'],
        created_at: '2024-01-01T08:00:00Z',
        completed_at: '2024-01-01T08:30:00Z',
        results_count: 25
      }
    ];

    const contextData: ContextData = {
      recent_domains: mockDomains,
      active_jobs: mockJobs,
      recent_urls: ['https://example.com', 'https://test.com'],
      timestamp: '2024-01-01T12:00:00Z'
    };

    const result: ChatContext = convertContextDataToChatContext(contextData);

    expect(result.current_domains).toEqual(['example.com', 'test.com']);
    expect(result.active_jobs).toEqual(['job1', 'job2']);
    expect(result.timestamp).toBe('2024-01-01T12:00:00Z');
  });

  it('should handle empty arrays gracefully', () => {
    const contextData: ContextData = {
      recent_domains: [],
      active_jobs: [],
      recent_urls: [],
      timestamp: '2024-01-01T12:00:00Z'
    };

    const result: ChatContext = convertContextDataToChatContext(contextData);

    expect(result.current_domains).toEqual([]);
    expect(result.active_jobs).toEqual([]);
    expect(result.timestamp).toBe('2024-01-01T12:00:00Z');
  });

  it('should handle undefined arrays gracefully', () => {
    const contextData: ContextData = {
      // recent_domains and active_jobs are omitted to be undefined
      recent_urls: [],
      timestamp: '2024-01-01T12:00:00Z'
    };

    const result: ChatContext = convertContextDataToChatContext(contextData);

    expect(result.active_jobs).toBeUndefined();
    expect(result.current_domains).toBeUndefined();
    expect(result.timestamp).toBe('2024-01-01T12:00:00Z');
  });

  it('should handle explicitly undefined arrays', () => {
    const contextData: ContextData = {
      recent_domains: undefined as any,
      active_jobs: undefined as any,
      recent_urls: [],
      timestamp: '2024-01-01T12:00:00Z'
    };

    const result: ChatContext = convertContextDataToChatContext(contextData);

    expect(result.active_jobs).toBeUndefined();
    expect(result.current_domains).toBeUndefined();
    expect(result.timestamp).toBe('2024-01-01T12:00:00Z');
  });

  it('should handle partial data correctly', () => {
    const mockDomains: Domain[] = [
      {
        id: 1,
        root_domain: 'example.com',
        subdomain: 'www.example.com',
        source: 'manual',
        tags: [],
        cdx_indexed: false,
        fetched_at: '2024-01-01T10:00:00Z'
      }
    ];

    const contextData: ContextData = {
      recent_domains: mockDomains,
      active_jobs: undefined,
      recent_urls: ['https://example.com'],
      timestamp: '2024-01-01T12:00:00Z'
    };

    const result: ChatContext = convertContextDataToChatContext(contextData);

    expect(result.current_domains).toEqual(['example.com']);
    expect(result.active_jobs).toBeUndefined();
    expect(result.timestamp).toBe('2024-01-01T12:00:00Z');
  });
});