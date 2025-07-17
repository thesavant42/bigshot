import React, { useState } from 'react';
import { TrashIcon, TagIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';

interface BulkActionsProps {
  selectedCount: number;
  onDelete: () => void;
  onTag: (tags: string[]) => void;
  onExport: () => void;
}

const BulkActions: React.FC<BulkActionsProps> = ({
  selectedCount,
  onDelete,
  onTag,
  onExport,
}) => {
  const [showTagInput, setShowTagInput] = useState(false);
  const [tagInput, setTagInput] = useState('');

  const handleTagSubmit = () => {
    if (tagInput.trim()) {
      const tags = tagInput.split(',').map(tag => tag.trim()).filter(Boolean);
      onTag(tags);
      setTagInput('');
      setShowTagInput(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleTagSubmit();
    } else if (e.key === 'Escape') {
      setShowTagInput(false);
      setTagInput('');
    }
  };

  return (
    <div className="flex items-center space-x-2 p-3 bg-gray-700 rounded-lg">
      <span className="text-sm text-gray-300">
        {selectedCount} domain{selectedCount !== 1 ? 's' : ''} selected
      </span>

      <div className="flex items-center space-x-2 ml-4">
        {/* Tag Action */}
        <div className="relative">
          {showTagInput ? (
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Enter tags (comma-separated)"
                className="px-3 py-1 bg-gray-600 text-white rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
              <button
                onClick={handleTagSubmit}
                className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                Apply
              </button>
              <button
                onClick={() => {
                  setShowTagInput(false);
                  setTagInput('');
                }}
                className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowTagInput(true)}
              className="flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <TagIcon className="h-4 w-4" />
              <span>Tag</span>
            </button>
          )}
        </div>

        {/* Export Action */}
        <button
          onClick={onExport}
          className="flex items-center space-x-1 px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          <ArrowDownTrayIcon className="h-4 w-4" />
          <span>Export</span>
        </button>

        {/* Delete Action */}
        <button
          onClick={onDelete}
          className="flex items-center space-x-1 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
        >
          <TrashIcon className="h-4 w-4" />
          <span>Delete</span>
        </button>
      </div>
    </div>
  );
};

export default BulkActions;