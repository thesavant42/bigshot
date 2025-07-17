import React, { useState, useEffect, useRef } from 'react';
import { ChatBubbleLeftRightIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useKeyboard } from '../contexts/KeyboardContext';
import ChatInterface from './ChatInterface';

interface SplitLayoutProps {
  leftPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  className?: string;
}

const SplitLayout: React.FC<SplitLayoutProps> = ({
  leftPanel,
  rightPanel,
  className = '',
}) => {
  const [leftWidth, setLeftWidth] = useState(40); // Percentage
  const [isDragging, setIsDragging] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const { addShortcut } = useKeyboard();

  // Check if mobile/tablet
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Add keyboard shortcuts
  useEffect(() => {
    addShortcut({
      key: 'c',
      ctrlKey: true,
      callback: () => setShowChat(!showChat),
      description: 'Toggle chat',
    });
  }, [addShortcut, showChat]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (isMobile) return;
    setIsDragging(true);
    e.preventDefault();
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging || isMobile) return;

    const container = containerRef.current;
    if (!container) return;

    const rect = container.getBoundingClientRect();
    const newLeftWidth = ((e.clientX - rect.left) / rect.width) * 100;
    
    // Constrain between 20% and 80%
    const constrainedWidth = Math.min(Math.max(newLeftWidth, 20), 80);
    setLeftWidth(constrainedWidth);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    if (!isMobile) return;
    setIsDragging(true);
    e.preventDefault();
  };

  const handleTouchMove = (e: TouchEvent) => {
    if (!isDragging || !isMobile) return;

    const container = containerRef.current;
    if (!container) return;

    const touch = e.touches[0];
    const rect = container.getBoundingClientRect();
    const newLeftWidth = ((touch.clientX - rect.left) / rect.width) * 100;
    
    const constrainedWidth = Math.min(Math.max(newLeftWidth, 20), 80);
    setLeftWidth(constrainedWidth);
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.addEventListener('touchmove', handleTouchMove);
      document.addEventListener('touchend', handleTouchEnd);
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.removeEventListener('touchmove', handleTouchMove);
        document.removeEventListener('touchend', handleTouchEnd);
      };
    }
  }, [isDragging]);

  // Mobile layout - stacked vertically
  if (isMobile) {
    return (
      <div className={`flex flex-col h-full relative ${className}`}>
        {/* Right Panel (Main content) */}
        <div className="flex-1 bg-gray-50 dark:bg-dark-950 overflow-hidden relative">
          {rightPanel}
          
          {/* Chat Toggle Button */}
          <button
            onClick={() => setShowChat(!showChat)}
            className="fixed bottom-6 right-6 p-4 bg-primary-600 text-white rounded-full shadow-strong hover:bg-primary-700 transition-colors z-30 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            title="Toggle AI Chat"
            aria-label="Toggle AI Chat"
          >
            <ChatBubbleLeftRightIcon className="h-6 w-6" />
          </button>

          {/* Chat Overlay */}
          {showChat && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end justify-center z-40">
              <div className="bg-white dark:bg-dark-800 rounded-t-xl shadow-strong w-full h-3/4 max-h-[80vh] animate-slide-in">
                <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">AI Assistant</h2>
                  <button
                    onClick={() => setShowChat(false)}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-700"
                    aria-label="Close chat"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
                <div className="h-full pb-16">
                  <ChatInterface className="h-full" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Left Panel (Minimized) */}
        <div className="flex-none bg-white dark:bg-dark-800 border-t border-gray-200 dark:border-gray-700 p-2">
          <div className="text-center">
            <button
              onClick={() => setShowChat(true)}
              className="text-primary-600 dark:text-primary-400 text-sm font-medium hover:text-primary-700 dark:hover:text-primary-300"
            >
              AI Assistant
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Desktop layout - side by side
  return (
    <div
      ref={containerRef}
      className={`flex h-full relative ${className}`}
      style={{ cursor: isDragging ? 'col-resize' : 'default' }}
    >
      {/* Left Panel */}
      <div
        className="flex-none bg-white dark:bg-dark-800 border-r border-gray-200 dark:border-gray-700 overflow-hidden"
        style={{ width: `${leftWidth}%` }}
      >
        {leftPanel}
      </div>

      {/* Resizer */}
      <div
        className="flex-none w-1 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 cursor-col-resize relative group transition-colors"
        onMouseDown={handleMouseDown}
        onTouchStart={handleTouchStart}
        role="separator"
        aria-orientation="vertical"
        aria-label="Resize panels"
        tabIndex={0}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-0.5 h-8 bg-gray-400 dark:bg-gray-500 group-hover:bg-gray-500 dark:group-hover:bg-gray-400 transition-colors"></div>
        </div>
      </div>

      {/* Right Panel */}
      <div
        className="flex-1 bg-gray-50 dark:bg-dark-950 overflow-hidden relative"
        style={{ width: `${100 - leftWidth}%` }}
      >
        {rightPanel}
      </div>
    </div>
  );
};

export default SplitLayout;