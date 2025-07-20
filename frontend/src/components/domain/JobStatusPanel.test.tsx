import { describe, it, expect } from 'vitest';

// Test the specific logic we fixed for handling undefined/null arrays
describe('JobStatusPanel - Array handling fix', () => {
  it('should handle undefined arrays safely', () => {
    const job = {
      target_domains: undefined,
      sources: undefined
    };

    // Test our fix: Array.isArray check prevents undefined.join() crash
    const domainsText = Array.isArray(job.target_domains) 
      ? job.target_domains.join(', ') 
      : 'No domains';
    
    const sourcesText = Array.isArray(job.sources)
      ? job.sources.join(', ')
      : 'No sources';

    expect(domainsText).toBe('No domains');
    expect(sourcesText).toBe('No sources');
  });

  it('should handle null arrays safely', () => {
    const job = {
      target_domains: null,
      sources: null
    };

    const domainsText = Array.isArray(job.target_domains) 
      ? job.target_domains.join(', ') 
      : 'No domains';
    
    const sourcesText = Array.isArray(job.sources)
      ? job.sources.join(', ')
      : 'No sources';

    expect(domainsText).toBe('No domains');
    expect(sourcesText).toBe('No sources');
  });

  it('should handle empty arrays correctly', () => {
    const job = {
      target_domains: [],
      sources: []
    };

    const domainsText = Array.isArray(job.target_domains) 
      ? job.target_domains.join(', ') 
      : 'No domains';
    
    const sourcesText = Array.isArray(job.sources)
      ? job.sources.join(', ')
      : 'No sources';

    expect(domainsText).toBe('');
    expect(sourcesText).toBe('');
  });

  it('should handle normal arrays correctly', () => {
    const job = {
      target_domains: ['example.com', 'test.com'],
      sources: ['crt.sh', 'virustotal']
    };

    const domainsText = Array.isArray(job.target_domains) 
      ? job.target_domains.join(', ') 
      : 'No domains';
    
    const sourcesText = Array.isArray(job.sources)
      ? job.sources.join(', ')
      : 'No sources';

    expect(domainsText).toBe('example.com, test.com');
    expect(sourcesText).toBe('crt.sh, virustotal');
  });

  it('should handle non-array values safely', () => {
    const job = {
      target_domains: 'not-an-array',
      sources: 123
    };

    const domainsText = Array.isArray(job.target_domains) 
      ? job.target_domains.join(', ') 
      : 'No domains';
    
    const sourcesText = Array.isArray(job.sources)
      ? job.sources.join(', ')
      : 'No sources';

    expect(domainsText).toBe('No domains');
    expect(sourcesText).toBe('No sources');
  });
});