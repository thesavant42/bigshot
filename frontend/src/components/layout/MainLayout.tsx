import React, { useState } from 'react';
import { Bars3Icon, XMarkIcon, ChartBarIcon, CogIcon, HeartIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useKeyboard } from '../../hooks/useKeyboard';
import ThemeToggle from '../ThemeToggle';
import StatusBadge from '../StatusBadge';
import SystemMonitoringDashboard from '../monitoring/SystemMonitoringDashboard';
import PostAuthProof from '../auth/PostAuthProof';
import ConfigurationManagement from '../monitoring/ConfigurationManagement';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [leftPanelWidth, setLeftPanelWidth] = useState(40); // Percentage
  const [activeView, setActiveView] = useState<'dashboard' | 'monitoring' | 'config' | 'health'>('dashboard');
  const { isConnected } = useWebSocket();
  const { addShortcut } = useKeyboard();

  // Add keyboard shortcuts
  React.useEffect(() => {
    addShortcut({
      key: 'b',
      ctrlKey: true,
      callback: () => setSidebarOpen(prev => !prev), // Use functional update to avoid stale closure
      description: 'Toggle sidebar',
    });

    // eslint-disable-next-line react-hooks/exhaustive-deps -- Only run once on mount to register shortcuts  
  }, []);

  const handleResize = (e: React.MouseEvent) => {
    const startX = e.clientX;
    const startWidth = leftPanelWidth;
    const containerWidth = window.innerWidth;

    const handleMouseMove = (e: MouseEvent) => {
      const deltaX = e.clientX - startX;
      const deltaPercent = (deltaX / containerWidth) * 100;
      const newWidth = Math.min(Math.max(20, startWidth + deltaPercent), 80);
      setLeftPanelWidth(newWidth);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <div className="flex h-screen bg-neutral-50 dark:bg-dark-950">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-dark-800 border-r border-neutral-200 dark:border-dark-700 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 shadow-medium lg:shadow-none`}
      >
        <div className="flex items-center justify-between h-16 px-4 bg-neutral-50 dark:bg-dark-900 border-b border-neutral-200 dark:border-dark-700">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-neutral-900 dark:text-white">BigShot</h1>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <ThemeToggle />
            <button
              className="lg:hidden p-2 rounded-lg text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-200"
              onClick={() => setSidebarOpen(false)}
              aria-label="Close sidebar"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        <nav className="mt-5 px-2">
          <div className="space-y-1">
            <button
              onClick={() => setActiveView('dashboard')}
              className={`w-full group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                activeView === 'dashboard'
                  ? 'bg-accent-100 dark:bg-accent-900/20 text-accent-900 dark:text-accent-100'
                  : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-dark-700 hover:text-neutral-900 dark:hover:text-white'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveView('monitoring')}
              className={`w-full group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                activeView === 'monitoring'
                  ? 'bg-accent-100 dark:bg-accent-900/20 text-accent-900 dark:text-accent-100'
                  : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-dark-700 hover:text-neutral-900 dark:hover:text-white'
              }`}
            >
              <ChartBarIcon className="h-5 w-5 mr-3" />
              System Metrics
            </button>
            <button
              onClick={() => setActiveView('health')}
              className={`w-full group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                activeView === 'health'
                  ? 'bg-accent-100 dark:bg-accent-900/20 text-accent-900 dark:text-accent-100'
                  : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-dark-700 hover:text-neutral-900 dark:hover:text-white'
              }`}
            >
              <HeartIcon className="h-5 w-5 mr-3" />
              Service Health
            </button>
            <button
              onClick={() => setActiveView('config')}
              className={`w-full group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                activeView === 'config'
                  ? 'bg-accent-100 dark:bg-accent-900/20 text-accent-900 dark:text-accent-100'
                  : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-dark-700 hover:text-neutral-900 dark:hover:text-white'
              }`}
            >
              <CogIcon className="h-5 w-5 mr-3" />
              Settings
            </button>
          </div>
        </nav>

        {/* Connection Status */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-neutral-200 dark:border-dark-700">
          <div className="flex items-center justify-between">
            <StatusBadge 
              status={isConnected ? 'success' : 'error'} 
              label={isConnected ? 'Connected' : 'Disconnected'}
              size="sm"
            />
            <kbd className="hidden sm:inline-flex items-center px-2 py-1 bg-neutral-100 dark:bg-dark-700 text-neutral-600 dark:text-neutral-400 text-xs rounded">
              Ctrl+B
            </kbd>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white dark:bg-dark-800 border-b border-neutral-200 dark:border-dark-700 shadow-soft">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <button
                  className="lg:hidden p-2 rounded-lg text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-200"
                  onClick={() => setSidebarOpen(true)}
                  aria-label="Open sidebar"
                >
                  <Bars3Icon className="h-5 w-5" />
                </button>
                {activeView !== 'dashboard' && (
                  <button
                    onClick={() => setActiveView('dashboard')}
                    className="flex items-center space-x-2 px-3 py-2 ml-2 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white rounded-lg transition-colors"
                    aria-label="Back to Dashboard"
                  >
                    <ArrowLeftIcon className="h-4 w-4" />
                    <span className="text-sm font-medium">Back to Dashboard</span>
                  </button>
                )}
                <div className="ml-4 flex items-center space-x-4">
                  {/* Global search removed - each section has its own contextual search */}
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="hidden lg:block">
                  <ThemeToggle />
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Split panel content */}
        <div className="flex-1 flex overflow-hidden">
          {activeView === 'dashboard' ? (
            <>
              {/* Left panel - Chat */}
              <div
                className="bg-white dark:bg-dark-800 border-r border-neutral-200 dark:border-dark-700 overflow-hidden"
                style={{ width: `${leftPanelWidth}%` }}
              >
                <div className="h-full flex flex-col">
                  <div className="flex-shrink-0 px-4 py-3 bg-neutral-50 dark:bg-dark-900 border-b border-neutral-200 dark:border-dark-700">
                    <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">AI Assistant</h2>
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <ChatInterface className="h-full" />
                  </div>
                </div>
              </div>

              {/* Resize handle */}
              <div
                className="w-1 bg-neutral-200 dark:bg-dark-700 hover:bg-neutral-300 dark:hover:bg-dark-600 cursor-col-resize transition-colors"
                onMouseDown={handleResize}
                role="separator"
                aria-orientation="vertical"
                aria-label="Resize panels"
              />

              {/* Right panel - Domain Dashboard */}
              <div className="flex-1 bg-neutral-50 dark:bg-dark-950 overflow-hidden">
                <div className="h-full flex flex-col">
                  <div className="flex-shrink-0 px-4 py-3 bg-white dark:bg-dark-800 border-b border-neutral-200 dark:border-dark-700">
                    <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">Domain Reconnaissance</h2>
                  </div>
                  <div className="flex-1 overflow-hidden">
                    {children}
                  </div>
                </div>
              </div>
            </>
          ) : (
            /* Full-width panels for monitoring, health, and config */
            <div className="flex-1 bg-neutral-50 dark:bg-dark-950 overflow-hidden">
              {activeView === 'monitoring' && <SystemMonitoringDashboard />}
              {activeView === 'health' && <PostAuthProof onContinue={() => setActiveView('dashboard')} />}
              {activeView === 'config' && <ConfigurationManagement />}
            </div>
          )}
        </div>
      </div>

      {/* Sidebar overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}
    </div>
  );
};

export default MainLayout;