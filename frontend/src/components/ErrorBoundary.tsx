import React, { Component, type ReactNode } from 'react';
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  retryKey: number;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, retryKey: 0 };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Update state to trigger the error UI
    return { hasError: true, error, retryKey: 0 };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log the error for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Call the optional onError callback
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleRetry = () => {
    // Reset the error state to allow retry and increment retryKey to force re-render
    this.setState(prevState => ({ 
      hasError: false, 
      error: null, 
      retryKey: prevState.retryKey + 1 
    }));
  };

  render() {
    if (this.state.hasError) {
      // Render custom fallback UI if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="flex flex-col items-center justify-center h-full p-8 text-center">
          <ExclamationTriangleIcon className="h-16 w-16 text-red-500 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Something went wrong
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
            An unexpected error occurred in the chat interface. We apologize for the inconvenience.
          </p>
          <div className="space-y-3">
            <button
              onClick={this.handleRetry}
              className="flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            >
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              Try Again
            </button>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              If the problem persists, please refresh the page or contact support.
            </p>
          </div>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details className="mt-6 w-full max-w-2xl">
              <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                Error Details (Development Only)
              </summary>
              <pre className="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-left text-xs overflow-auto max-h-64">
                {this.state.error.toString()}
                {this.state.error.stack && '\n\n' + this.state.error.stack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return <div key={this.state.retryKey}>{this.props.children}</div>;
  }
}

export default ErrorBoundary;