import React, { useState } from 'react';
import { Bars3Icon, XMarkIcon, MagnifyingGlassIcon, ChartBarIcon, CogIcon, HeartIcon } from '@heroicons/react/24/outline';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useKeyboard } from '../../hooks/useKeyboard';
import ThemeToggle from '../ThemeToggle';
import StatusBadge from '../StatusBadge';
import ChatInterface from '../chat/ChatInterface';
import SystemMonitoringDashboard from '../monitoring/SystemMonitoringDashboard';
import ConfigurationManagement from '../monitoring/ConfigurationManagement';
import PostAuthProof from '../auth/PostAuthProof';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [leftPanelWidth, setLeftPanelWidth] = useState(40); // Percentage
  const [searchQuery, setSearchQuery] = useState('');
  const [activeView, setActiveView] = useState<'dashboard' | 'monitoring' | 'config' | 'health'>('dashboard');
  const { isConnected } = useWebSocket();
  const { addShortcut } = useKeyboard();

  // Add keyboard shortcuts
  React.useEffect(() => {
    addShortcut({
      key: 'k',
      ctrlKey: true,
      callback: () => {
        const searchInput = document.getElementById('search-input');
        searchInput?.focus();
      },
      description: 'Focus search',
    });

    // eslint-disable-next-line react-hooks/exhaustive-deps -- Only run once on mount to register shortcuts
  }, []);

  // Separate effect for sidebar toggle to avoid render loop
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
    <div className="flex h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-dark-950 dark:to-dark-900">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-dark-800 border-r border-gray-200 dark:border-gray-700 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 shadow-strong lg:shadow-none backdrop-blur-lg bg-opacity-95 dark:bg-opacity-95`}
      >
        <div className="flex items-center justify-between h-16 px-4 bg-gradient-to-r from-primary-600 to-primary-700 border-b border-primary-500">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center mr-3">
                <span className="text-primary-600 font-bold text-lg">B</span>
              </div>
              <h1 className="text-xl font-bold text-white">BigShot</h1>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <ThemeToggle />
            <button
              className="lg:hidden p-2 rounded-lg text-white/80 hover:text-white hover:bg-white/10"
              onClick={() => setSidebarOpen(false)}
              aria-label="Close sidebar"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        <nav className="mt-6 px-3">
          <div className="space-y-2">
            <button
              onClick={() => setActiveView('dashboard')}
              className={`w-full group flex items-center px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-200 ${
                activeView === 'dashboard'
                  ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-medium'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveView('monitoring')}
              className={`w-full group flex items-center px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-200 ${
                activeView === 'monitoring'
                  ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-medium'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <ChartBarIcon className="h-5 w-5 mr-3" />
              Monitoring
            </button>
            <button
              onClick={() => setActiveView('config')}
              className={`w-full group flex items-center px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-200 ${
                activeView === 'config'
                  ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-medium'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <CogIcon className="h-5 w-5 mr-3" />
              Settings
            </button>
            <button
              onClick={() => setActiveView('health')}
              className={`w-full group flex items-center px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-200 ${
                activeView === 'health'
                  ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-medium'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <HeartIcon className="h-5 w-5 mr-3" />
              Health Status
            </button>
          </div>
        </nav>

        {/* Connection Status */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <StatusBadge 
              status={isConnected ? 'success' : 'error'} 
              label={isConnected ? 'Connected' : 'Disconnected'}
              size="sm"
            />
            <kbd className="hidden sm:inline-flex items-center px-2 py-1 bg-gray-100 dark:bg-dark-700 text-gray-600 dark:text-gray-400 text-xs rounded">
              Ctrl+B
            </kbd>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white dark:bg-dark-800 border-b border-gray-200 dark:border-gray-700 shadow-soft backdrop-blur-lg bg-opacity-95 dark:bg-opacity-95">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <button
                  className="lg:hidden p-2 rounded-xl text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-dark-700 transition-all duration-200"
                  onClick={() => setSidebarOpen(true)}
                  aria-label="Open sidebar"
                >
                  <Bars3Icon className="h-5 w-5" />
                </button>
                <div className="ml-4 flex items-center space-x-4">
                  <div className="relative">
                    <input
                      id="search-input"
                      type="search"
                      placeholder="Search domains..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-64 pl-10 pr-16 py-2.5 bg-gray-50 dark:bg-dark-700 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 font-medium placeholder-gray-500 dark:placeholder-gray-400"
                    />
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                      <kbd className="hidden sm:inline-flex items-center px-2 py-1 bg-gray-200 dark:bg-dark-600 text-gray-600 dark:text-gray-400 text-xs rounded-lg font-medium">
                        Ctrl+K
                      </kbd>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-gray-600 dark:text-gray-400 text-sm font-medium">
                    Ready for reconnaissance
                  </span>
                </div>
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
                className="bg-white dark:bg-dark-800 border-r border-gray-200 dark:border-gray-700 overflow-hidden shadow-soft"
                style={{ width: `${leftPanelWidth}%` }}
              >
                <div className="h-full flex flex-col">
                  <div className="flex-shrink-0 px-6 py-4 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-dark-900 dark:to-dark-800 border-b border-gray-200 dark:border-gray-700">
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center">
                      <div className="w-2 h-2 bg-primary-500 rounded-full mr-3"></div>
                      AI Assistant
                    </h2>
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <ChatInterface className="h-full" />
                  </div>
                </div>
              </div>

              {/* Resize handle */}
              <div
                className="w-1 bg-gray-200 dark:bg-gray-700 hover:bg-primary-400 dark:hover:bg-primary-500 cursor-col-resize transition-colors duration-200"
                onMouseDown={handleResize}
                role="separator"
                aria-orientation="vertical"
                aria-label="Resize panels"
              />

              {/* Right panel - Domain Dashboard */}
              <div className="flex-1 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-dark-950 dark:to-dark-900 overflow-hidden">
                <div className="h-full flex flex-col">
                  <div className="flex-shrink-0 px-6 py-4 bg-white dark:bg-dark-800 border-b border-gray-200 dark:border-gray-700 shadow-soft">
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center">
                      <div className="w-2 h-2 bg-success-500 rounded-full mr-3"></div>
                      Domain Reconnaissance
                    </h2>
                  </div>
                  <div className="flex-1 overflow-hidden">
                    {children}
                  </div>
                </div>
              </div>
            </>
          ) : (
            /* Full-width panels for monitoring, config, and health */
            <div className="flex-1 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-dark-950 dark:to-dark-900 overflow-hidden">
              {activeView === 'monitoring' && <SystemMonitoringDashboard />}
              {activeView === 'config' && <ConfigurationManagement />}
              {activeView === 'health' && <PostAuthProof onContinue={() => setActiveView('dashboard')} />}
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