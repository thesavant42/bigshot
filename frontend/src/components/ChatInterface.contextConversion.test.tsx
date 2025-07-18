import { describe, it, expect } from 'vitest';
import type { ContextData, ChatContext, Job, Domain } from '../types';

// Helper function to simulate the context conversion logic
const convertContextDataToChatContext = (contextData: ContextData): ChatContext => {
  return {
    current_domains: contextData.recent_domains?.map(d => d.root_domain),
    active_jobs: contextData.active_jobs?.map(j => j.id),
    timestamp: contextData.timestamp
  };
};

describe('ChatInterface Context Conversion', () => {
  it('should correctly convert ContextData to ChatContext', () => {
    // Sample data matching the types from the codebase
    const mockJobs: Job[] = [
      {
        id: 'job-1',
        type: 'subdomain_enum',
        status: 'running',
        target_domains: ['example.com'],
        sources: ['crtsh'],
        created_at: '2024-01-01T00:00:00Z',
        progress: 50
      },
      {
        id: 'job-2',
        type: 'port_scan',
        status: 'completed',
        target_domains: ['test.com'],
        sources: ['nmap'],
        created_at: '2024-01-01T01:00:00Z',
        completed_at: '2024-01-01T01:30:00Z',
        results_count: 10
      }
    ];

    const mockDomains: Domain[] = [
      {
        id: 1,
        root_domain: 'example.com',
        subdomain: 'www.example.com',
        source: 'crtsh',
        tags: ['target'],
        cdx_indexed: true,
        fetched_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 2,
        root_domain: 'test.com',
        subdomain: 'api.test.com',
        source: 'subfinder',
        tags: ['api'],
        cdx_indexed: false,
        fetched_at: '2024-01-01T01:00:00Z'
      }
    ];

    const contextData: ContextData = {
      recent_domains: mockDomains,
      active_jobs: mockJobs,
      recent_urls: ['https://example.com', 'https://test.com'],
      timestamp: '2024-01-01T12:00:00Z'
    };

    const result: ChatContext = convertContextDataToChatContext(contextData);

    // Verify the conversion from Job[] to string[]
    expect(result.active_jobs).toEqual(['job-1', 'job-2']);
    expect(result.active_jobs).toHaveLength(2);
    expect(typeof result.active_jobs![0]).toBe('string');
    expect(typeof result.active_jobs![1]).toBe('string');

    // Verify the conversion from Domain[] to string[]
    expect(result.current_domains).toEqual(['example.com', 'test.com']);
    expect(result.current_domains).toHaveLength(2);
    expect(typeof result.current_domains![0]).toBe('string');
    expect(typeof result.current_domains![1]).toBe('string');

    // Verify timestamp is preserved
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

    expect(result.active_jobs).toEqual([]);
    expect(result.current_domains).toEqual([]);
    expect(result.timestamp).toBe('2024-01-01T12:00:00Z');
  });

  it('should handle undefined arrays gracefully', () => {
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
});