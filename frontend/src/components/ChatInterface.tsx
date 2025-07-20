import React, { useState, useEffect, useRef } from 'react';
import { PaperAirplaneIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { chatService, type ChatMessage, type ChatContext } from '../services/chatService';

interface ChatInterfaceProps {
  className?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ className = '' }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [context] = useState<ChatContext>({});
  const [isServiceAvailable, setIsServiceAvailable] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    
    // Check chat service availability
    const checkServiceAvailability = async () => {
      try {
        if (isMountedRef.current) {
          const status = await chatService.getStatus();
          setIsServiceAvailable(status.available);
          if (!status.available) {
            setError("Chat service is not available");
          } else {
            setError(null);
          }
        }
      } catch (err) {
        console.error('Failed to check chat service availability:', err);
        if (isMountedRef.current) {
          setIsServiceAvailable(false);
          setError("Failed to connect to chat service");
        }
      }
    };

    checkServiceAvailability();

    return () => {
      isMountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const retryConnection = async () => {
    setError(null);
    setIsServiceAvailable(false);
    
    try {
      const status = await chatService.getStatus();
      setIsServiceAvailable(status.available);
      if (!status.available) {
        setError("Chat service is not available");
      }
    } catch (err) {
      console.error('Failed to retry chat service connection:', err);
      setIsServiceAvailable(false);
      setError("Failed to connect to chat service");
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading || !isServiceAvailable) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsStreaming(true);

      await chatService.createStreamingChat(
        inputMessage,
        messages,
        context,
        (chunk) => {
          // Handle streaming chunk
          if (chunk.content) {
            setMessages(prev => {
              const newMessages = [...prev];
              const lastMessage = newMessages[newMessages.length - 1];
              if (lastMessage.role === 'assistant') {
                lastMessage.content += chunk.content;
              }
              return newMessages;
            });
          }
        },
        () => {
          // Handle completion
          setIsStreaming(false);
          setIsLoading(false);
        },
        (error) => {
          // Handle error
          setError(error.message);
          setIsStreaming(false);
          setIsLoading(false);
        }
      );
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An error occurred');
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const renderMessage = (message: ChatMessage, index: number) => {
    const isUser = message.role === 'user';
    const isAssistant = message.role === 'assistant';

    return (
      <div key={index} className={`mb-4 ${isUser ? 'text-right' : 'text-left'}`}>
        <div
          className={`inline-block max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
            isUser
              ? 'bg-blue-500 text-white'
              : isAssistant
              ? 'bg-gray-200 text-gray-900'
              : 'bg-gray-100 text-gray-600'
          }`}
        >
          <div className="whitespace-pre-wrap break-words">
            {message.content}
          </div>
          {message.function_calls && message.function_calls.length > 0 && (
            <div className="mt-2 text-xs opacity-75">
              <div className="font-semibold">Function calls:</div>
              {message.function_calls.map((call, i) => (
                <div key={i} className="mt-1">
                  {call.name}: {JSON.stringify(call.arguments)}
                </div>
              ))}
            </div>
          )}
        </div>
        {message.created_at && (
          <div className="text-xs text-gray-500 mt-1">
            {new Date(message.created_at).toLocaleTimeString()}
          </div>
        )}
      </div>
    );
  };

  if (!isServiceAvailable) {
    return (
      <div className={`flex flex-col h-full ${className}`}>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <ExclamationTriangleIcon className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Chat Service Temporarily Disabled
            </h3>
            <p className="text-gray-600">
              Chat functionality is currently unavailable. Please check your LLM provider configuration.
            </p>
            <button
              onClick={retryConnection}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="flex-none p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">AI Assistant</h2>
        <p className="text-sm text-gray-600">
          Ask questions about your reconnaissance data
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>Start a conversation with your AI assistant!</p>
            <p className="text-sm mt-2">
              Try asking: "What domains have been discovered recently?"
            </p>
          </div>
        ) : (
          messages.map((message, index) => renderMessage(message, index))
        )}
        
        {isStreaming && (
          <div className="text-left">
            <div className="inline-block bg-gray-200 text-gray-900 px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-pulse">Thinking...</div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="flex-none p-4 bg-red-50 border-t border-red-200">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Input */}
      <div className="flex-none p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about your reconnaissance data..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading || !isServiceAvailable}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim() || !isServiceAvailable}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
            ) : (
              <PaperAirplaneIcon className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;