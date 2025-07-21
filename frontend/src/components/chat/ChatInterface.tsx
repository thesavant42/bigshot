import React, { useState, useRef, useEffect } from 'react';
import { useChat, useAvailableModels, useLLMProviders } from '../../hooks/useApi';
import { useChatUpdates } from '../../hooks/useWebSocket';
import ChatHeader from './ChatHeader';
import ChatMessages from './ChatMessages';
import ChatInput from './ChatInput';
import type { LMStudioModel } from '../../types';

interface ChatInterfaceProps {
  className?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ className = '' }) => {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(1000);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { sendMessage, conversation, isLoading } = useChat();
  const { activeProvider } = useLLMProviders();
  const { data: modelsData } = useAvailableModels(!!activeProvider);
  const chatUpdates = useChatUpdates();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation, chatUpdates]);

  // Set default model when models are loaded (using useRef to prevent infinite loops)
  const hasSetDefaultModel = useRef(false);
  
  useEffect(() => {
    if (modelsData?.models && Array.isArray(modelsData.models) && modelsData.models.length > 0 && !selectedModel && !hasSetDefaultModel.current) {
      let defaultModel = '';
      
      // If models is an array of objects (detailed), get the first model's ID
      if (typeof modelsData.models[0] === 'object' && (modelsData.models[0] as LMStudioModel).id) {
        defaultModel = (modelsData.models[0] as LMStudioModel).id;
      } 
      // If models is an array of strings (simple), get the first model
      else if (typeof modelsData.models[0] === 'string') {
        defaultModel = modelsData.models[0];
      }
      
      if (defaultModel) {
        setSelectedModel(defaultModel);
        hasSetDefaultModel.current = true;
      }
    }
  }, [modelsData?.models, selectedModel]); // Include selectedModel to avoid stale closure issues

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

  const messages = Array.isArray(conversation) ? conversation : [];

  return (
    <div className={`flex flex-col h-full ${className}`}>
      <ChatHeader
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
        models={modelsData?.models}
        modelsLoading={!modelsData?.models}
        activeProvider={activeProvider}
        showSettings={showSettings}
        onToggleSettings={() => setShowSettings(!showSettings)}
        temperature={temperature}
        onTemperatureChange={setTemperature}
        maxTokens={maxTokens}
        onMaxTokensChange={setMaxTokens}
      />

      <ChatMessages
        messages={messages}
        isTyping={isTyping}
        messagesEndRef={messagesEndRef}
      />

      <ChatInput
        message={message}
        onMessageChange={setMessage}
        onSubmit={handleSubmit}
        isLoading={isLoading}
        isTyping={isTyping}
      />
    </div>
  );
};

export default ChatInterface;