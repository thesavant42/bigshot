import React, { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import type { FilterOptions } from '../../types';

interface FilterModalProps {
  filters: FilterOptions;
  onClose: () => void;
  onApply: (filters: FilterOptions) => void;
}

const FilterModal: React.FC<FilterModalProps> = ({ filters, onClose, onApply }) => {
  const [localFilters, setLocalFilters] = useState<FilterOptions>(filters);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onApply(localFilters);
    onClose();
  };

  const handleReset = () => {
    const resetFilters = { page: 1, per_page: 100 };
    setLocalFilters(resetFilters);
    onApply(resetFilters);
    onClose();
  };

  const sources = ['crt.sh', 'virustotal', 'shodan'];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Filter Domains</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Root Domain Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Root Domain
            </label>
            <input
              type="text"
              value={localFilters.root_domain || ''}
              onChange={(e) => setLocalFilters(prev => ({ ...prev, root_domain: e.target.value || undefined }))}
              placeholder="example.com"
              className="w-full px-3 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Source Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Source
            </label>
            <select
              value={localFilters.source || ''}
              onChange={(e) => setLocalFilters(prev => ({ ...prev, source: e.target.value || undefined }))}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All sources</option>
              {sources.map(source => (
                <option key={source} value={source}>{source}</option>
              ))}
            </select>
          </div>

          {/* Per Page */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Results per page
            </label>
            <select
              value={localFilters.per_page || 100}
              onChange={(e) => setLocalFilters(prev => ({ ...prev, per_page: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
              <option value={500}>500</option>
            </select>
          </div>

          {/* Actions */}
          <div className="flex justify-between pt-4">
            <button
              type="button"
              onClick={handleReset}
              className="px-4 py-2 text-sm font-medium text-gray-300 bg-gray-700 rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Reset
            </button>
            <div className="flex space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-300 bg-gray-700 rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FilterModal;