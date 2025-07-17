import React, { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface AddDomainModalProps {
  onClose: () => void;
  onEnumerate: (domains: string[], sources: string[]) => void;
}

const AddDomainModal: React.FC<AddDomainModalProps> = ({ onClose, onEnumerate }) => {
  const [domainsInput, setDomainsInput] = useState('');
  const [selectedSources, setSelectedSources] = useState<string[]>(['crt.sh']);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const availableSources = [
    { id: 'crt.sh', name: 'Certificate Transparency (crt.sh)', description: 'SSL certificate logs' },
    { id: 'virustotal', name: 'VirusTotal', description: 'Passive DNS resolution' },
    { id: 'shodan', name: 'Shodan', description: 'Internet-connected devices' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!domainsInput.trim() || selectedSources.length === 0) return;

    setIsSubmitting(true);

    try {
      const domains = domainsInput
        .split('\n')
        .map(line => line.trim())
        .filter(Boolean)
        .map(domain => domain.replace(/^https?:\/\//, '').replace(/\/.*$/, ''));

      await onEnumerate(domains, selectedSources);
      onClose();
    } catch (error) {
      console.error('Failed to start enumeration:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSourceToggle = (sourceId: string) => {
    setSelectedSources(prev => 
      prev.includes(sourceId)
        ? prev.filter(id => id !== sourceId)
        : [...prev, sourceId]
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Start Domain Enumeration</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Domain Input */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Target Domains
            </label>
            <textarea
              value={domainsInput}
              onChange={(e) => setDomainsInput(e.target.value)}
              placeholder="example.com&#10;target.org&#10;test.net"
              className="w-full px-3 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={4}
              required
            />
            <p className="text-xs text-gray-400 mt-1">
              Enter one domain per line
            </p>
          </div>

          {/* Source Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Enumeration Sources
            </label>
            <div className="space-y-2">
              {availableSources.map(source => (
                <label
                  key={source.id}
                  className="flex items-start space-x-3 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedSources.includes(source.id)}
                    onChange={() => handleSourceToggle(source.id)}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-white">
                      {source.name}
                    </div>
                    <div className="text-xs text-gray-400">
                      {source.description}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-300 bg-gray-700 rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !domainsInput.trim() || selectedSources.length === 0}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Starting...' : 'Start Enumeration'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddDomainModal;