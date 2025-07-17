import type { Domain, TreeNode } from '../types';

export const buildDomainTree = (domains: Domain[]): TreeNode[] => {
  const tree: TreeNode[] = [];
  const nodeMap: Map<string, TreeNode> = new Map();

  // Sort domains by subdomain for consistent ordering
  const sortedDomains = [...domains].sort((a, b) => a.subdomain.localeCompare(b.subdomain));

  sortedDomains.forEach(domain => {
    const parts = domain.subdomain.split('.').reverse(); // Reverse for root-first processing
    let currentLevel = tree;
    let currentPath = '';

    parts.forEach((part, index) => {
      currentPath = index === 0 ? part : `${part}.${currentPath}`;
      const nodeId = currentPath;

      let node = nodeMap.get(nodeId);
      if (!node) {
        node = {
          id: nodeId,
          label: part,
          children: [],
          level: index,
          isExpanded: index < 2, // Auto-expand first 2 levels
        };

        // If this is the final part, attach the domain data
        if (index === parts.length - 1) {
          node.data = domain;
        }

        nodeMap.set(nodeId, node);
        currentLevel.push(node);
      }

      currentLevel = node.children;
    });
  });

  return tree;
};

export const flattenTree = (tree: TreeNode[]): TreeNode[] => {
  const result: TreeNode[] = [];
  
  const traverse = (nodes: TreeNode[], level: number = 0) => {
    nodes.forEach(node => {
      const nodeWithLevel = { ...node, level };
      result.push(nodeWithLevel);
      
      if (node.isExpanded && node.children.length > 0) {
        traverse(node.children, level + 1);
      }
    });
  };
  
  traverse(tree);
  return result;
};

export const toggleNode = (tree: TreeNode[], nodeId: string): TreeNode[] => {
  const toggle = (nodes: TreeNode[]): TreeNode[] => {
    return nodes.map(node => {
      if (node.id === nodeId) {
        return { ...node, isExpanded: !node.isExpanded };
      }
      if (node.children.length > 0) {
        return { ...node, children: toggle(node.children) };
      }
      return node;
    });
  };
  
  return toggle(tree);
};

export const expandNode = (tree: TreeNode[], nodeId: string): TreeNode[] => {
  const expand = (nodes: TreeNode[]): TreeNode[] => {
    return nodes.map(node => {
      if (node.id === nodeId) {
        return { ...node, isExpanded: true };
      }
      if (node.children.length > 0) {
        return { ...node, children: expand(node.children) };
      }
      return node;
    });
  };
  
  return expand(tree);
};

export const collapseNode = (tree: TreeNode[], nodeId: string): TreeNode[] => {
  const collapse = (nodes: TreeNode[]): TreeNode[] => {
    return nodes.map(node => {
      if (node.id === nodeId) {
        return { ...node, isExpanded: false };
      }
      if (node.children.length > 0) {
        return { ...node, children: collapse(node.children) };
      }
      return node;
    });
  };
  
  return collapse(tree);
};

export const findNodeById = (tree: TreeNode[], nodeId: string): TreeNode | null => {
  for (const node of tree) {
    if (node.id === nodeId) {
      return node;
    }
    if (node.children.length > 0) {
      const found = findNodeById(node.children, nodeId);
      if (found) {
        return found;
      }
    }
  }
  return null;
};

export const filterTree = (tree: TreeNode[], searchTerm: string): TreeNode[] => {
  if (!searchTerm) return tree;
  
  const filter = (nodes: TreeNode[]): TreeNode[] => {
    return nodes.reduce((filtered: TreeNode[], node) => {
      const matchesSearch = node.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           node.data?.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const filteredChildren = filter(node.children);
      
      if (matchesSearch || filteredChildren.length > 0) {
        filtered.push({
          ...node,
          children: filteredChildren,
          isExpanded: true, // Auto-expand when filtering
        });
      }
      
      return filtered;
    }, []);
  };
  
  return filter(tree);
};

export const getSelectedDomains = (tree: TreeNode[], selectedIds: Set<string>): Domain[] => {
  const domains: Domain[] = [];
  
  const traverse = (nodes: TreeNode[]) => {
    nodes.forEach(node => {
      if (selectedIds.has(node.id) && node.data) {
        domains.push(node.data);
      }
      traverse(node.children);
    });
  };
  
  traverse(tree);
  return domains;
};

export const formatDomainDisplay = (domain: Domain): string => {
  return domain.subdomain;
};

export const getDomainIcon = (domain: Domain): string => {
  // Return appropriate icon based on domain properties
  if (domain.cdx_indexed) {
    return 'check-circle';
  }
  if (domain.source === 'crt.sh') {
    return 'shield-check';
  }
  if (domain.source === 'virustotal') {
    return 'exclamation-triangle';
  }
  if (domain.source === 'shodan') {
    return 'search';
  }
  return 'globe';
};

export const getDomainColor = (domain: Domain): string => {
  // Return color class based on domain properties
  if (domain.cdx_indexed) {
    return 'text-green-600';
  }
  if (domain.source === 'virustotal') {
    return 'text-yellow-600';
  }
  if (domain.source === 'shodan') {
    return 'text-blue-600';
  }
  return 'text-gray-600';
};