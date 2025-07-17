import React, { useState } from 'react';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import { useWebSocket } from '../../hooks/useWebSocket';
import ChatInterface from '../chat/ChatInterface';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [leftPanelWidth, setLeftPanelWidth] = useState(40); // Percentage
  const { isConnected } = useWebSocket();

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
    <div className="flex h-screen bg-gray-900">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } fixed inset-y-0 left-0 z-50 w-64 bg-gray-800 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}
      >
        <div className="flex items-center justify-between h-16 px-4 bg-gray-900">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-white">BigShot</h1>
            </div>
          </div>
          <button
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <XMarkIcon className="h-6 w-6 text-gray-400" />
          </button>
        </div>

        <nav className="mt-5 px-2">
          <div className="space-y-1">
            <a
              href="#"
              className="bg-gray-900 text-white group flex items-center px-2 py-2 text-sm font-medium rounded-md"
            >
              Dashboard
            </a>
            <a
              href="#"
              className="text-gray-300 hover:bg-gray-700 hover:text-white group flex items-center px-2 py-2 text-sm font-medium rounded-md"
            >
              Jobs
            </a>
            <a
              href="#"
              className="text-gray-300 hover:bg-gray-700 hover:text-white group flex items-center px-2 py-2 text-sm font-medium rounded-md"
            >
              Settings
            </a>
          </div>
        </nav>

        {/* Connection Status */}
        <div className="absolute bottom-0 left-0 right-0 p-4">
          <div className="flex items-center space-x-2">
            <div
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`}
            />
            <span className="text-sm text-gray-400">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-gray-800 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <button
                  className="lg:hidden"
                  onClick={() => setSidebarOpen(true)}
                >
                  <Bars3Icon className="h-6 w-6 text-gray-400" />
                </button>
                <div className="ml-4 flex items-center space-x-4">
                  <div className="relative">
                    <input
                      type="search"
                      placeholder="Search domains..."
                      className="w-64 pl-10 pr-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-gray-400 text-sm">
                  Ready for reconnaissance
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Split panel content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left panel - Chat */}
          <div
            className="bg-gray-800 border-r border-gray-700 overflow-hidden"
            style={{ width: `${leftPanelWidth}%` }}
          >
            <div className="h-full flex flex-col">
              <div className="flex-shrink-0 px-4 py-3 bg-gray-900 border-b border-gray-700">
                <h2 className="text-lg font-semibold text-white">AI Assistant</h2>
              </div>
              <div className="flex-1 overflow-hidden">
                <ChatInterface className="h-full" />
              </div>
            </div>
          </div>

          {/* Resize handle */}
          <div
            className="w-1 bg-gray-600 hover:bg-gray-500 cursor-col-resize"
            onMouseDown={handleResize}
          />

          {/* Right panel - Domain Dashboard */}
          <div className="flex-1 bg-gray-900 overflow-hidden">
            <div className="h-full flex flex-col">
              <div className="flex-shrink-0 px-4 py-3 bg-gray-800 border-b border-gray-700">
                <h2 className="text-lg font-semibold text-white">Domain Reconnaissance</h2>
              </div>
              <div className="flex-1 overflow-hidden">
                {children}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sidebar overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default MainLayout;