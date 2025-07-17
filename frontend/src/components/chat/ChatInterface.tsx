import React, { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, UserIcon, BeakerIcon } from '@heroicons/react/24/outline';
import { useChat } from '../../hooks/useApi';
import { useChatUpdates } from '../../hooks/useWebSocket';
import type { ChatMessage } from '../../types';

interface ChatInterfaceProps {
  className?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ className = '' }) => {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { sendMessage, conversation, isLoading } = useChat();
  const chatUpdates = useChatUpdates();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation, chatUpdates]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    const userMessage = message;
    setMessage('');
    setIsTyping(true);

    try {
      await sendMessage.mutateAsync({ message: userMessage });
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsTyping(false);
    }
  };

  const formatMessage = (content: string) => {
    // Basic markdown-like formatting
    return content
      .replace(/```(.*?)```/gs, '<pre class="bg-gray-800 p-3 rounded-lg overflow-x-auto"><code>$1</code></pre>')
      .replace(/`([^`]+)`/g, '<code class="bg-gray-800 px-2 py-1 rounded text-sm">$1</code>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  };

  const messages = conversation || [];

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <BeakerIcon className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-400">
              Start a conversation with your AI assistant
            </p>
            <p className="text-gray-500 text-sm mt-2">
              Ask about domain enumeration, analyze results, or get help with reconnaissance
            </p>
          </div>
        ) : (
          messages.map((msg: ChatMessage) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-3 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                {/* Avatar */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-600'
                }`}>
                  {msg.role === 'user' ? (
                    <UserIcon className="h-5 w-5 text-white" />
                  ) : (
                    <BeakerIcon className="h-5 w-5 text-white" />
                  )}
                </div>

                {/* Message */}
                <div className={`rounded-lg p-3 ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-700 text-gray-100'
                }`}>
                  <div 
                    className="text-sm"
                    dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }}
                  />
                  <div className="text-xs mt-2 opacity-70">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
                <BeakerIcon className="h-5 w-5 text-white" />
              </div>
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="border-t border-gray-700 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
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
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            onClick={() => setMessage('What domains have been discovered recently?')}
            className="px-3 py-1 bg-gray-700 text-gray-300 rounded-lg text-sm hover:bg-gray-600"
          >
            Recent discoveries
          </button>
          <button
            onClick={() => setMessage('Show me the domain hierarchy for example.com')}
            className="px-3 py-1 bg-gray-700 text-gray-300 rounded-lg text-sm hover:bg-gray-600"
          >
            Domain hierarchy
          </button>
          <button
            onClick={() => setMessage('Start enumeration for target.com')}
            className="px-3 py-1 bg-gray-700 text-gray-300 rounded-lg text-sm hover:bg-gray-600"
          >
            Start enumeration
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;