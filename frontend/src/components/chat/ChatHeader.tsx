import React from 'react';
import { CogIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import type { LMStudioModel, LLMProviderConfig } from '../../types';

interface ChatHeaderProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
  models?: (string | LMStudioModel)[];
  modelsLoading?: boolean;
  activeProvider?: LLMProviderConfig;
  showSettings: boolean;
  onToggleSettings: () => void;
  temperature: number;
  onTemperatureChange: (temp: number) => void;
  maxTokens: number;
  onMaxTokensChange: (tokens: number) => void;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({
  selectedModel,
  onModelChange,
  models,
  modelsLoading,
  activeProvider,
  showSettings,
  onToggleSettings,
  temperature,
  onTemperatureChange,
  maxTokens,
  onMaxTokensChange
}) => {
  return (
    <div className="border-b border-gray-700 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* Model Selection */}
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-400">Model:</label>
            {modelsLoading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                <span className="text-sm text-gray-400">Loading models...</span>
              </div>
            ) : !models || models.length === 0 ? (
              <div className="flex items-center space-x-2 px-3 py-1 bg-gray-700 text-red-400 rounded border border-gray-600 text-sm">
                <span>⚠️ No models available</span>
              </div>
            ) : (
              <select
                value={selectedModel}
                onChange={(e) => onModelChange(e.target.value)}
                className="px-3 py-1 bg-gray-700 text-white rounded border border-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {models.map((model: string | LMStudioModel) => {
                  const modelId = typeof model === 'string' ? model : model.id;
                  const modelName = typeof model === 'string' ? model : (model.displayName || model.id);
                  return (
                    <option key={modelId} value={modelId}>
                      {modelName}
                    </option>
                  );
                })}
              </select>
            )}
          </div>

          {/* Provider Info */}
          {activeProvider && (
            <div className="text-xs text-gray-500">
              Provider: {activeProvider.name}
            </div>
          )}
        </div>

        {/* Settings Toggle */}
        <button
          onClick={onToggleSettings}
          className="flex items-center space-x-1 px-3 py-1 text-gray-400 hover:text-white transition-colors"
        >
          <CogIcon className="h-4 w-4" />
          <span className="text-sm">Settings</span>
          <ChevronDownIcon className={`h-4 w-4 transition-transform ${showSettings ? 'rotate-180' : ''}`} />
        </button>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="mt-4 p-4 bg-gray-800 rounded-lg space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {/* Temperature */}
            <div>
              <label className="block text-sm text-gray-400 mb-1">
                Temperature: {temperature}
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={temperature}
                onChange={(e) => onTemperatureChange(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Conservative</span>
                <span>Creative</span>
              </div>
            </div>

            {/* Max Tokens */}
            <div>
              <label className="block text-sm text-gray-400 mb-1">
                Max Tokens: {maxTokens}
              </label>
              <input
                type="range"
                min="100"
                max="4000"
                step="100"
                value={maxTokens}
                onChange={(e) => onMaxTokensChange(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>100</span>
                <span>4000</span>
              </div>
            </div>
          </div>

          {/* Model Info */}
          {models && selectedModel && (
            <div className="text-xs text-gray-500">
              <div>Selected Model: {selectedModel}</div>
              {activeProvider && (
                <div>Provider: {activeProvider.name || 'Unknown'}</div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ChatHeader;