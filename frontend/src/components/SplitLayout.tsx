import React, { useState } from 'react';
import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
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
  const [leftWidth, setLeftWidth] = useState(30); // Percentage
  const [isDragging, setIsDragging] = useState(false);
  const [showChat, setShowChat] = useState(false);

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    e.preventDefault();
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return;

    const container = document.getElementById('split-container');
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

  React.useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging]);

  return (
    <div
      id="split-container"
      className={`flex h-full relative ${className}`}
      style={{ cursor: isDragging ? 'col-resize' : 'default' }}
    >
      {/* Left Panel */}
      <div
        className="flex-none bg-white border-r border-gray-200 overflow-hidden"
        style={{ width: `${leftWidth}%` }}
      >
        {leftPanel}
      </div>

      {/* Resizer */}
      <div
        className="flex-none w-1 bg-gray-200 hover:bg-gray-300 cursor-col-resize relative group"
        onMouseDown={handleMouseDown}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-0.5 h-8 bg-gray-400 group-hover:bg-gray-500 transition-colors"></div>
        </div>
      </div>

      {/* Right Panel */}
      <div
        className="flex-1 bg-white overflow-hidden relative"
        style={{ width: `${100 - leftWidth}%` }}
      >
        {rightPanel}
        
        {/* Chat Toggle Button */}
        <button
          onClick={() => setShowChat(!showChat)}
          className="absolute bottom-4 right-4 p-3 bg-blue-500 text-white rounded-full shadow-lg hover:bg-blue-600 transition-colors z-10"
          title="Toggle AI Chat"
        >
          <ChatBubbleLeftRightIcon className="h-6 w-6" />
        </button>

        {/* Chat Overlay */}
        {showChat && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-20">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl h-3/4 m-4">
              <div className="flex items-center justify-between p-4 border-b">
                <h2 className="text-lg font-semibold">AI Assistant</h2>
                <button
                  onClick={() => setShowChat(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="h-full">
                <ChatInterface className="h-full" />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SplitLayout;