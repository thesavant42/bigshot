import React, { useState, useEffect } from 'react';
import { 
  MagnifyingGlassIcon,
  FunnelIcon,
  PlusIcon,
  PlayIcon,
  StopIcon
} from '@heroicons/react/24/outline';
import { useDomains, useJobs } from '../../hooks/useApi';
import { useDomainUpdates } from '../../hooks/useWebSocket';
import type { Domain, FilterOptions } from '../../types';
import DomainTree from './DomainTree';
import BulkActions from './BulkActions';
import AddDomainModal from './AddDomainModal';
import FilterModal from './FilterModal';
import JobStatusPanel from './JobStatusPanel';

const DomainDashboard: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDomains, setSelectedDomains] = useState<Set<string>>(new Set());
  const [filters, setFilters] = useState<FilterOptions>({
    page: 1,
    per_page: 100,
  });
  const [showAddModal, setShowAddModal] = useState(false);
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [showJobPanel, setShowJobPanel] = useState(false);

  const { domains, isLoading, error, enumerateDomains, bulkOperation, refetch } = useDomains(filters);
  const { jobs } = useJobs();
  const domainUpdates = useDomainUpdates();

  // Refetch domains when new ones are discovered
  useEffect(() => {
    if (domainUpdates.length > 0) {
      refetch();
    }
  }, [domainUpdates, refetch]);

  // Apply search filter
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setFilters(prev => ({ ...prev, search: searchTerm || undefined, page: 1 }));
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm]);

  const handleSelectionChange = (selectedIds: Set<string>) => {
    setSelectedDomains(selectedIds);
  };

  const handleDomainClick = (domain: Domain) => {
    console.log('Domain clicked:', domain);
    // TODO: Implement domain detail view
  };

  const handleBulkDelete = async () => {
    if (selectedDomains.size === 0) return;

    const domainIds = Array.from(selectedDomains).map(id => {
      const domain = domains?.data?.find((d: Domain) => d.subdomain === id);
      return domain?.id;
    }).filter(Boolean) as number[];

    try {
      await bulkOperation.mutateAsync({
        operation: 'delete',
        domainIds,
      });
      setSelectedDomains(new Set());
    } catch (error) {
      console.error('Bulk delete failed:', error);
    }
  };

  const handleBulkTag = async (tags: string[]) => {
    if (selectedDomains.size === 0) return;

    const domainIds = Array.from(selectedDomains).map(id => {
      const domain = domains?.data?.find((d: Domain) => d.subdomain === id);
      return domain?.id;
    }).filter(Boolean) as number[];

    try {
      await bulkOperation.mutateAsync({
        operation: 'update_tags',
        domainIds,
        data: { tags },
      });
      setSelectedDomains(new Set());
    } catch (error) {
      console.error('Bulk tag failed:', error);
    }
  };

  const handleEnumerate = async (targetDomains: string[], sources: string[]) => {
    try {
      await enumerateDomains.mutateAsync({
        domains: targetDomains,
        sources,
        options: {},
      });
      setShowJobPanel(true);
    } catch (error) {
      console.error('Enumeration failed:', error);
    }
  };

  const handleExport = () => {
    const domainsToExport = selectedDomains.size > 0 
      ? domains?.data?.filter((d: Domain) => selectedDomains.has(d.subdomain))
      : domains?.data;

    if (!domainsToExport || domainsToExport.length === 0) return;

    const csvContent = [
      ['Domain', 'Root Domain', 'Source', 'Tags', 'CDX Indexed', 'Discovered'],
      ...domainsToExport.map((d: Domain) => [
        d.subdomain,
        d.root_domain,
        d.source,
        d.tags.join(';'),
        d.cdx_indexed ? 'Yes' : 'No',
        d.fetched_at,
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `domains-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const runningJobs = jobs?.filter(job => job.status === 'running') || [];
  const completedJobs = jobs?.filter(job => job.status === 'completed') || [];

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="flex-shrink-0 bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search domains..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
              />
            </div>

            {/* Filters */}
            <button
              onClick={() => setShowFilterModal(true)}
              className="flex items-center space-x-2 px-3 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <FunnelIcon className="h-4 w-4" />
              <span>Filters</span>
            </button>

            {/* Add Domain */}
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-4 w-4" />
              <span>Add Domain</span>
            </button>
          </div>

          <div className="flex items-center space-x-4">
            {/* Job Status */}
            <div className="flex items-center space-x-2">
              {runningJobs.length > 0 && (
                <span className="flex items-center space-x-1 text-yellow-400">
                  <PlayIcon className="h-4 w-4" />
                  <span className="text-sm">{runningJobs.length} running</span>
                </span>
              )}
              {completedJobs.length > 0 && (
                <span className="flex items-center space-x-1 text-green-400">
                  <StopIcon className="h-4 w-4" />
                  <span className="text-sm">{completedJobs.length} completed</span>
                </span>
              )}
              <button
                onClick={() => setShowJobPanel(true)}
                className="text-blue-400 hover:text-blue-300 text-sm"
              >
                View Jobs
              </button>
            </div>

            {/* Domain Count */}
            <span className="text-gray-400 text-sm">
              {domains?.data?.length || 0} domains
              {selectedDomains.size > 0 && ` (${selectedDomains.size} selected)`}
            </span>
          </div>
        </div>

        {/* Bulk Actions */}
        {selectedDomains.size > 0 && (
          <div className="mt-4 flex items-center space-x-2">
            <BulkActions
              selectedCount={selectedDomains.size}
              onDelete={handleBulkDelete}
              onTag={handleBulkTag}
              onExport={handleExport}
            />
          </div>
        )}
      </div>

      {/* Domain Tree */}
      <div className="flex-1 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-red-400">Error loading domains: {error.message}</div>
          </div>
        ) : (
          <DomainTree
            domains={domains?.data || []}
            selectedIds={selectedDomains}
            onSelectionChange={handleSelectionChange}
            onDomainClick={handleDomainClick}
            searchTerm={searchTerm}
            className="h-full p-4"
          />
        )}
      </div>

      {/* Pagination */}
      {domains?.pagination && domains.pagination.pages > 1 && (
        <div className="flex-shrink-0 bg-gray-800 border-t border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-400">
              Showing {((domains.pagination.page - 1) * domains.pagination.per_page) + 1} to{' '}
              {Math.min(domains.pagination.page * domains.pagination.per_page, domains.pagination.total)} of{' '}
              {domains.pagination.total} results
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setFilters(prev => ({ ...prev, page: (prev.page || 1) - 1 }))}
                disabled={domains.pagination.page === 1}
                className="px-3 py-1 bg-gray-700 text-white rounded disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-sm text-gray-400">
                Page {domains.pagination.page} of {domains.pagination.pages}
              </span>
              <button
                onClick={() => setFilters(prev => ({ ...prev, page: (prev.page || 1) + 1 }))}
                disabled={domains.pagination.page === domains.pagination.pages}
                className="px-3 py-1 bg-gray-700 text-white rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modals */}
      {showAddModal && (
        <AddDomainModal
          onClose={() => setShowAddModal(false)}
          onEnumerate={handleEnumerate}
        />
      )}

      {showFilterModal && (
        <FilterModal
          filters={filters}
          onClose={() => setShowFilterModal(false)}
          onApply={setFilters}
        />
      )}

      {showJobPanel && (
        <JobStatusPanel
          onClose={() => setShowJobPanel(false)}
        />
      )}
    </div>
  );
};

export default DomainDashboard;