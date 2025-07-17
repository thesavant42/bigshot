# BigShot Frontend Architecture

## Overview

The BigShot frontend is a modern React application built with TypeScript and Tailwind CSS that provides a professional interface for domain reconnaissance activities. It follows a component-based architecture with clear separation of concerns and integrates seamlessly with the Flask backend API.

## Technology Stack

- **React 18** - Modern React with hooks and functional components
- **TypeScript** - Type safety and better development experience
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Server state management and caching
- **Socket.io** - Real-time WebSocket communication
- **Axios** - HTTP client for API calls
- **Heroicons** - Beautiful SVG icons

## Architecture Overview

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── layout/          # Layout components
│   │   ├── domain/          # Domain-related components
│   │   ├── chat/            # Chat interface components
│   │   └── common/          # Shared components
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API and WebSocket services
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   └── App.tsx              # Main application component
```

## Key Components

### MainLayout
- **Purpose**: Provides the main application layout with split-panel interface
- **Features**:
  - Resizable panels for chat and domain dashboard
  - Responsive sidebar navigation
  - Global search functionality
  - WebSocket connection status indicator
- **Location**: `src/components/layout/MainLayout.tsx`

### DomainDashboard
- **Purpose**: Main interface for domain reconnaissance activities
- **Features**:
  - Domain search and filtering
  - Bulk operations (delete, tag, export)
  - Job status monitoring
  - Pagination support
- **Location**: `src/components/domain/DomainDashboard.tsx`

### DomainTree
- **Purpose**: Hierarchical display of domains with collapsible tree structure
- **Features**:
  - Expandable/collapsible domain hierarchy
  - Multi-selection support
  - Domain metadata display (source, tags, status)
  - Keyboard navigation
- **Location**: `src/components/domain/DomainTree.tsx`

### ChatInterface
- **Purpose**: AI assistant chat interface with context awareness
- **Features**:
  - Message history
  - Markdown rendering
  - Quick action buttons
  - Real-time message streaming
- **Location**: `src/components/chat/ChatInterface.tsx`

### JobStatusPanel
- **Purpose**: Monitor and manage background enumeration jobs
- **Features**:
  - Real-time job progress tracking
  - Job cancellation
  - Error handling and logging
  - Status indicators
- **Location**: `src/components/domain/JobStatusPanel.tsx`

## State Management

### React Query
- Used for server state management and caching
- Automatic background refetching
- Optimistic updates for better UX
- Error handling and retry logic

### Custom Hooks
- `useAuth`: Authentication state and operations
- `useDomains`: Domain data management
- `useJobs`: Job status and operations
- `useWebSocket`: Real-time updates

## API Integration

### REST API Service
- **Location**: `src/services/api.ts`
- **Features**:
  - Axios-based HTTP client
  - Request/response interceptors
  - Automatic token handling
  - Type-safe API calls

### WebSocket Service
- **Location**: `src/services/websocket.ts`
- **Features**:
  - Real-time job updates
  - Domain discovery notifications
  - Chat message streaming
  - Connection management

## Type System

### Core Types
- `Domain`: Domain entity with metadata
- `Job`: Background job representation
- `ChatMessage`: Chat message structure
- `TreeNode`: Hierarchical tree node
- `FilterOptions`: Search and filter parameters

### API Types
- `ApiResponse<T>`: Standard API response wrapper
- `PaginatedResponse<T>`: Paginated data response
- `WebSocketMessage`: Real-time message structure

## UI Design System

### Color Scheme
- Dark theme by default
- Professional gray palette
- Accent colors for status indicators
- Consistent color usage across components

### Typography
- System fonts for better performance
- Consistent font sizes and weights
- Proper line heights for readability

### Responsive Design
- Mobile-first approach
- Breakpoint-based layout adjustments
- Touch-friendly interactions

## Development Workflow

### Building
```bash
cd frontend
npm install
npm run build
```

### Development Server
```bash
npm run dev
```

### Testing
```bash
npm run test
```

### Linting
```bash
npm run lint
```

## Performance Considerations

### Code Splitting
- Dynamic imports for large components
- Route-based code splitting
- Lazy loading for non-critical features

### Optimization
- Memoization for expensive calculations
- Virtual scrolling for large lists
- Image optimization and lazy loading

### Caching
- React Query caching for API responses
- Service worker for offline capabilities
- Browser caching for static assets

## Security Features

### Authentication
- JWT token-based authentication
- Automatic token refresh
- Secure token storage

### Input Validation
- Client-side validation
- XSS protection
- CSRF protection

### API Security
- Request signing
- Rate limiting
- CORS configuration

## Testing Strategy

### Unit Tests
- Component testing with React Testing Library
- Hook testing with custom test utilities
- Service testing with mocked dependencies

### Integration Tests
- API integration testing
- WebSocket communication testing
- User workflow testing

### E2E Tests
- Critical path testing
- Cross-browser compatibility
- Performance testing

## Accessibility

### WCAG Compliance
- ARIA labels and roles
- Keyboard navigation
- Screen reader support
- Color contrast compliance

### Usability
- Intuitive navigation
- Clear visual hierarchy
- Responsive interactions
- Error handling and feedback

## Deployment

### Production Build
- Optimized bundle size
- Tree shaking for unused code
- Asset optimization
- Environment configuration

### Environment Variables
- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_WS_URL`: WebSocket server URL
- `REACT_APP_ENV`: Environment identifier

## Future Enhancements

### Planned Features
- Advanced domain analytics
- Export to various formats
- Custom dashboard widgets
- Enhanced search capabilities

### Technical Improvements
- Service worker implementation
- Progressive Web App features
- Advanced caching strategies
- Performance monitoring

## Troubleshooting

### Common Issues
1. **Build Failures**: Check Node.js version compatibility
2. **API Connection**: Verify backend server is running
3. **WebSocket Issues**: Check firewall and proxy settings
4. **Type Errors**: Ensure TypeScript dependencies are updated

### Debug Tools
- React Developer Tools
- Network tab for API debugging
- Console logging for WebSocket events
- Performance profiler for optimization

## Contributing

### Code Style
- Follow existing naming conventions
- Use TypeScript for type safety
- Write comprehensive tests
- Document complex logic

### Pull Request Process
1. Create feature branch
2. Implement changes with tests
3. Update documentation
4. Submit PR with clear description

This documentation provides a comprehensive overview of the BigShot frontend architecture and serves as a guide for developers working on the project.