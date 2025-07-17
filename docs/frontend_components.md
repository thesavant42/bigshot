# BigShot Component Reference

## Layout Components

### MainLayout
**File**: `src/components/layout/MainLayout.tsx`

A responsive layout component that provides the main application structure with split panels.

**Props**:
- `children: React.ReactNode` - Content to render in the main panel

**Features**:
- Resizable split panels (chat + main content)
- Collapsible sidebar navigation
- Global search bar
- WebSocket connection status indicator
- Mobile-responsive design

**Usage**:
```tsx
<MainLayout>
  <DomainDashboard />
</MainLayout>
```

## Domain Components

### DomainDashboard
**File**: `src/components/domain/DomainDashboard.tsx`

Main dashboard interface for domain reconnaissance activities.

**Features**:
- Domain search and filtering
- Bulk operations (delete, tag, export)
- Job status monitoring
- Pagination support
- Real-time updates via WebSocket

**State**:
- Search term
- Selected domains
- Filter options
- Modal visibility states

**Key Methods**:
- `handleBulkDelete()` - Delete multiple domains
- `handleBulkTag()` - Tag multiple domains
- `handleExport()` - Export domain data to CSV
- `handleEnumerate()` - Start domain enumeration

### DomainTree
**File**: `src/components/domain/DomainTree.tsx`

Hierarchical tree view for displaying domain structure.

**Props**:
- `domains: Domain[]` - Array of domain objects
- `selectedIds: Set<string>` - Currently selected domain IDs
- `onSelectionChange: (ids: Set<string>) => void` - Selection change handler
- `onDomainClick?: (domain: Domain) => void` - Domain click handler
- `searchTerm: string` - Current search term for filtering
- `className?: string` - Additional CSS classes

**Features**:
- Expandable/collapsible tree structure
- Multi-selection with checkboxes
- Domain metadata display (source, tags, status)
- Search-based filtering
- Keyboard navigation support

**Usage**:
```tsx
<DomainTree
  domains={domains}
  selectedIds={selectedIds}
  onSelectionChange={setSelectedIds}
  onDomainClick={handleDomainClick}
  searchTerm={searchTerm}
/>
```

### BulkActions
**File**: `src/components/domain/BulkActions.tsx`

Action bar for performing bulk operations on selected domains.

**Props**:
- `selectedCount: number` - Number of selected domains
- `onDelete: () => void` - Delete action handler
- `onTag: (tags: string[]) => void` - Tag action handler
- `onExport: () => void` - Export action handler

**Features**:
- Inline tag input with comma separation
- Export selected domains to CSV
- Delete confirmation
- Visual feedback for actions

### AddDomainModal
**File**: `src/components/domain/AddDomainModal.tsx`

Modal dialog for starting new domain enumeration jobs.

**Props**:
- `onClose: () => void` - Close modal handler
- `onEnumerate: (domains: string[], sources: string[]) => void` - Enumeration handler

**Features**:
- Multi-line domain input
- Source selection (crt.sh, VirusTotal, Shodan)
- Input validation
- Loading states

### FilterModal
**File**: `src/components/domain/FilterModal.tsx`

Modal dialog for advanced domain filtering options.

**Props**:
- `filters: FilterOptions` - Current filter state
- `onClose: () => void` - Close modal handler
- `onApply: (filters: FilterOptions) => void` - Apply filters handler

**Features**:
- Root domain filtering
- Source filtering
- Results per page selection
- Filter reset functionality

### JobStatusPanel
**File**: `src/components/domain/JobStatusPanel.tsx`

Panel for monitoring and managing background enumeration jobs.

**Props**:
- `onClose: () => void` - Close panel handler

**Features**:
- Real-time job progress tracking
- Job status indicators
- Job cancellation
- Error display
- Job history

## Chat Components

### ChatInterface
**File**: `src/components/chat/ChatInterface.tsx`

AI assistant chat interface with context awareness.

**Props**:
- `className?: string` - Additional CSS classes

**Features**:
- Message history display
- Markdown rendering for AI responses
- Quick action buttons
- Real-time message streaming
- Typing indicators
- Context-aware responses

**State**:
- Current message input
- Typing state
- Message history

**Usage**:
```tsx
<ChatInterface className="h-full" />
```

## Utility Functions

### Domain Tree Utils
**File**: `src/utils/domainTree.ts`

Utility functions for working with domain tree structures.

**Functions**:

#### `buildDomainTree(domains: Domain[]): TreeNode[]`
Builds a hierarchical tree structure from flat domain array.

#### `flattenTree(tree: TreeNode[]): TreeNode[]`
Flattens tree structure for rendering while respecting expansion state.

#### `toggleNode(tree: TreeNode[], nodeId: string): TreeNode[]`
Toggles expansion state of a specific node.

#### `filterTree(tree: TreeNode[], searchTerm: string): TreeNode[]`
Filters tree nodes based on search term.

#### `getSelectedDomains(tree: TreeNode[], selectedIds: Set<string>): Domain[]`
Extracts domain objects from selected tree nodes.

#### `getDomainIcon(domain: Domain): string`
Returns appropriate icon name for domain based on properties.

#### `getDomainColor(domain: Domain): string`
Returns CSS color class for domain based on properties.

## Custom Hooks

### useAuth
**File**: `src/hooks/useApi.ts`

Authentication hook for managing user login state.

**Returns**:
- `login: UseMutationResult` - Login mutation
- `logout: () => void` - Logout function
- `isAuthenticated: boolean` - Authentication status
- `isLoading: boolean` - Loading state

### useDomains
**File**: `src/hooks/useApi.ts`

Hook for managing domain data and operations.

**Parameters**:
- `filters?: FilterOptions` - Optional filter options

**Returns**:
- `domains: PaginatedResponse<Domain>` - Domain data
- `isLoading: boolean` - Loading state
- `error: Error | null` - Error state
- `createDomain: UseMutationResult` - Create domain mutation
- `updateDomain: UseMutationResult` - Update domain mutation
- `deleteDomain: UseMutationResult` - Delete domain mutation
- `bulkOperation: UseMutationResult` - Bulk operation mutation
- `enumerateDomains: UseMutationResult` - Enumeration mutation
- `refetch: () => void` - Refetch function

### useJobs
**File**: `src/hooks/useApi.ts`

Hook for managing background job operations.

**Returns**:
- `jobs: Job[]` - Array of jobs
- `isLoading: boolean` - Loading state
- `error: Error | null` - Error state
- `cancelJob: UseMutationResult` - Cancel job mutation
- `refetch: () => void` - Refetch function

### useWebSocket
**File**: `src/hooks/useWebSocket.ts`

Hook for managing WebSocket connections and real-time updates.

**Returns**:
- `isConnected: boolean` - Connection status
- `subscribe: (event: string, handler: Function) => () => void` - Subscribe to events
- `sendMessage: (type: string, data: any) => void` - Send message

### useJobUpdates
**File**: `src/hooks/useWebSocket.ts`

Hook for receiving real-time job updates.

**Returns**:
- `jobUpdates: any[]` - Array of recent job updates

### useDomainUpdates
**File**: `src/hooks/useWebSocket.ts`

Hook for receiving real-time domain discovery updates.

**Returns**:
- `domainUpdates: any[]` - Array of recent domain updates

## Services

### API Service
**File**: `src/services/api.ts`

HTTP client service for backend API communication.

**Key Methods**:
- `login(username, password)` - User authentication
- `getDomains(filters)` - Fetch domains with filtering
- `createDomain(domain)` - Create new domain
- `updateDomain(id, updates)` - Update domain
- `deleteDomain(id)` - Delete domain
- `bulkDomainOperation(operation, ids, data)` - Bulk operations
- `enumerateDomains(domains, sources, options)` - Start enumeration
- `getJobs()` - Fetch jobs
- `cancelJob(id)` - Cancel job
- `sendMessage(message, context)` - Send chat message

### WebSocket Service
**File**: `src/services/websocket.ts`

WebSocket service for real-time communication.

**Key Methods**:
- `connect(url)` - Establish WebSocket connection
- `disconnect()` - Close WebSocket connection
- `subscribe(event, handler)` - Subscribe to events
- `sendMessage(type, data)` - Send message
- `joinRoom(room)` - Join room for targeted updates
- `leaveRoom(room)` - Leave room

## Type Definitions

### Domain
```typescript
interface Domain {
  id: number;
  root_domain: string;
  subdomain: string;
  source: string;
  tags: string[];
  cdx_indexed: boolean;
  fetched_at: string;
}
```

### Job
```typescript
interface Job {
  id: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  target_domains: string[];
  sources: string[];
  created_at: string;
  completed_at?: string;
  results_count?: number;
  progress?: number;
  error?: string;
}
```

### TreeNode
```typescript
interface TreeNode {
  id: string;
  label: string;
  children: TreeNode[];
  data?: Domain;
  isExpanded?: boolean;
  level: number;
}
```

### FilterOptions
```typescript
interface FilterOptions {
  search?: string;
  root_domain?: string;
  source?: string;
  tags?: string[];
  page?: number;
  per_page?: number;
}
```

## Testing

### Component Testing
Each component includes comprehensive tests covering:
- Rendering behavior
- User interactions
- Props handling
- State management
- Error conditions

### Example Test Structure
```typescript
describe('ComponentName', () => {
  it('renders correctly', () => {
    // Test rendering
  });
  
  it('handles user interactions', () => {
    // Test click handlers, form submissions, etc.
  });
  
  it('manages state correctly', () => {
    // Test state updates
  });
});
```

### Testing Utilities
- React Testing Library for component testing
- Jest for test framework
- Mock API responses for isolated testing
- Custom test utilities for common patterns

This reference provides detailed information about each component, hook, and service in the BigShot frontend application.