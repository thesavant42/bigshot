import React, { useState, useEffect } from 'react';
import { 
  ChevronRightIcon, 
  ChevronDownIcon,
  GlobeAltIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';
import type { Domain, TreeNode } from '../../types';
import { 
  buildDomainTree, 
  flattenTree, 
  toggleNode, 
  filterTree, 
  getDomainIcon, 
  getDomainColor 
} from '../../utils/domainTree';

interface DomainTreeProps {
  domains: Domain[];
  selectedIds: Set<string>;
  onSelectionChange: (selectedIds: Set<string>) => void;
  onDomainClick?: (domain: Domain) => void;
  searchTerm: string;
  className?: string;
}

const iconMap = {
  'globe': GlobeAltIcon,
  'check-circle': CheckCircleIcon,
  'shield-check': ShieldCheckIcon,
  'exclamation-triangle': ExclamationTriangleIcon,
  'search': MagnifyingGlassIcon,
};

const DomainTree: React.FC<DomainTreeProps> = ({
  domains,
  selectedIds,
  onSelectionChange,
  onDomainClick,
  searchTerm,
  className = ''
}) => {
  const [tree, setTree] = useState<TreeNode[]>([]);
  const [flattenedTree, setFlattenedTree] = useState<TreeNode[]>([]);

  useEffect(() => {
    const domainTree = buildDomainTree(domains);
    const filteredTree = filterTree(domainTree, searchTerm);
    setTree(filteredTree);
    setFlattenedTree(flattenTree(filteredTree));
  }, [domains, searchTerm]);

  const handleToggle = (nodeId: string) => {
    const newTree = toggleNode(tree, nodeId);
    setTree(newTree);
    setFlattenedTree(flattenTree(newTree));
  };

  const handleSelection = (nodeId: string, isSelected: boolean) => {
    const newSelection = new Set(selectedIds);
    if (isSelected) {
      newSelection.add(nodeId);
    } else {
      newSelection.delete(nodeId);
    }
    onSelectionChange(newSelection);
  };

  const handleDomainClick = (node: TreeNode) => {
    if (node.data && onDomainClick) {
      onDomainClick(node.data);
    }
  };

  const renderNode = (node: TreeNode) => {
    const hasChildren = node.children.length > 0;
    const isSelected = selectedIds.has(node.id);
    const iconName = node.data ? getDomainIcon(node.data) : 'globe';
    const IconComponent = iconMap[iconName as keyof typeof iconMap];
    const colorClass = node.data ? getDomainColor(node.data) : 'text-gray-400';
    
    return (
      <div
        key={node.id}
        className={`flex items-center py-1 px-2 hover:bg-gray-800 rounded ${
          isSelected ? 'bg-gray-700' : ''
        }`}
        style={{ paddingLeft: `${node.level * 20 + 8}px` }}
      >
        {/* Expand/Collapse Toggle */}
        <button
          onClick={() => handleToggle(node.id)}
          className={`mr-2 p-1 rounded ${
            hasChildren ? 'text-gray-400 hover:text-white' : 'invisible'
          }`}
        >
          {hasChildren ? (
            node.isExpanded ? (
              <ChevronDownIcon className="h-4 w-4" />
            ) : (
              <ChevronRightIcon className="h-4 w-4" />
            )
          ) : (
            <div className="h-4 w-4" />
          )}
        </button>

        {/* Selection Checkbox */}
        {node.data && (
          <input
            type="checkbox"
            checked={isSelected}
            onChange={(e) => handleSelection(node.id, e.target.checked)}
            className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
        )}

        {/* Domain Icon */}
        <IconComponent className={`h-4 w-4 mr-2 ${colorClass}`} />

        {/* Domain Label */}
        <span
          className={`flex-1 text-sm cursor-pointer ${
            node.data ? 'text-white hover:text-blue-300' : 'text-gray-300'
          }`}
          onClick={() => handleDomainClick(node)}
        >
          {node.label}
        </span>

        {/* Domain Metadata */}
        {node.data && (
          <div className="flex items-center space-x-2 ml-2">
            {/* Source Badge */}
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-700 text-gray-300">
              {node.data.source}
            </span>

            {/* Tags */}
            {node.data.tags && node.data.tags.length > 0 && (
              <div className="flex space-x-1">
                {node.data.tags.slice(0, 2).map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-600 text-white"
                  >
                    {tag}
                  </span>
                ))}
                {node.data.tags.length > 2 && (
                  <span className="text-xs text-gray-400">
                    +{node.data.tags.length - 2}
                  </span>
                )}
              </div>
            )}

            {/* CDX Indexed Indicator */}
            {node.data.cdx_indexed && (
              <CheckCircleIcon className="h-4 w-4 text-green-500" title="CDX Indexed" />
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`${className} overflow-auto`}>
      {flattenedTree.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          {searchTerm ? 'No domains match your search' : 'No domains found'}
        </div>
      ) : (
        <div className="space-y-1">
          {flattenedTree.map(renderNode)}
        </div>
      )}
    </div>
  );
};

export default DomainTree;