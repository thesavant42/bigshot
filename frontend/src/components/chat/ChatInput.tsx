import React from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/outline';
import QuickActionButtons from '../QuickActionButtons';

interface ChatInputProps {
  message: string;
  onMessageChange: (message: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
  isTyping: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  message,
  onMessageChange,
  onSubmit,
  isLoading,
  isTyping
}) => {
  return (
    <div className="border-t border-gray-700 p-4">
      <form onSubmit={onSubmit} className="flex space-x-2">
        <input
          type="text"
          value={message}
          onChange={(e) => onMessageChange(e.target.value)}
          placeholder="Ask about domains, start enumeration, or get help..."
          className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading || isTyping}
        />
        <button
          type="submit"
          disabled={!message.trim() || isLoading || isTyping}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <PaperAirplaneIcon className="h-5 w-5" />
        </button>
      </form>
      
      {/* Quick Actions */}
      <QuickActionButtons 
        onButtonClick={onMessageChange}
        className="mt-3"
      />
    </div>
  );
};

export default ChatInput;