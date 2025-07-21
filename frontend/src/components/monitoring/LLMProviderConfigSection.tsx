import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  PlusIcon, 
  TrashIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  CloudIcon,
  ComputerDesktopIcon,
  BeakerIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { apiService } from '../../services/api';
import LoadingSpinner from '../LoadingSpinner';
import StatusBadge from '../StatusBadge';
import type { LLMProviderConfig, LLMProviderConfigInput, LLMProviderPreset } from '../../types';

/**
 * LLM Provider Configuration Section
 * 
 * This component allows users to manage LLM provider configurations for runtime switching.
 * 
 * Previous Issue (Fixed):
 * Users reported that LMStudio config edits were not saving/reflecting in the UI.
 * This was caused by React infinite render loops in WebSocket hooks and chat polling,
 * which interfered with form state management and UI updates.
 * 
 * Resolution:
 * - Fixed useWebSocket hooks to prevent infinite re-renders by removing unstable dependencies
 * - Reduced aggressive polling intervals (chat refetch from 5s to 30s, WebSocket check from 1s to 10s)  
 * - Added refetchOnWindowFocus: false to prevent unwanted refetches
 * 
 * The backend API functionality was never broken - only the frontend UI state management.
 */

interface ProviderFormData extends LLMProviderConfigInput {
  id?: number;
}

const LLMProviderConfigSection: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingProvider, setEditingProvider] = useState<LLMProviderConfig | null>(null);
  const [formData, setFormData] = useState<ProviderFormData>({
    provider: 'lmstudio',
    name: '',
    base_url: '',
    api_key: '',
    model: '',
    connection_timeout: 30,
    max_tokens: 8000,
    temperature: 0.7,
  });
  const [testingProvider, setTestingProvider] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const { data: providers = [], isLoading: providersLoading } = useQuery({
    queryKey: ['llm-providers'],
    queryFn: () => apiService.getLLMProviders(),
  });

  const { data: activeProvider } = useQuery({
    queryKey: ['llm-providers', 'active'],
    queryFn: () => apiService.getActiveLLMProvider(),
    retry: false,
  });

  const { data: presets = [] } = useQuery({
    queryKey: ['llm-providers', 'presets'],
    queryFn: () => apiService.getLLMProviderPresets(),
  });

  const { data: auditLogs = [] } = useQuery({
    queryKey: ['llm-providers', 'audit-logs'],
    queryFn: () => apiService.getLLMProviderAuditLogs(10),
  });

  const createProviderMutation = useMutation({
    mutationFn: (provider: LLMProviderConfigInput) => apiService.createLLMProvider(provider),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['llm-providers'] });
      setShowForm(false);
      setFormData({
        provider: 'lmstudio',
        name: '',
        base_url: '',
        api_key: '',
        model: '',
        connection_timeout: 30,
        max_tokens: 8000,
        temperature: 0.7,
      });
    },
  });

  const updateProviderMutation = useMutation({
    mutationFn: ({ id, updates }: { id: number; updates: Partial<LLMProviderConfigInput> }) =>
      apiService.updateLLMProvider(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['llm-providers'] });
      setEditingProvider(null);
      setShowForm(false);
    },
  });

  const deleteProviderMutation = useMutation({
    mutationFn: (id: number) => apiService.deleteLLMProvider(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['llm-providers'] });
    },
  });

  const activateProviderMutation = useMutation({
    mutationFn: (id: number) => apiService.activateLLMProvider(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['llm-providers'] });
      queryClient.invalidateQueries({ queryKey: ['llm-providers', 'active'] });
      queryClient.invalidateQueries({ queryKey: ['llm-providers', 'audit-logs'] });
    },
  });

  const testProviderMutation = useMutation({
    mutationFn: (id: number) => apiService.testLLMProvider(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['llm-providers', 'audit-logs'] });
      setTestingProvider(null);
    },
    onError: () => {
      setTestingProvider(null);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingProvider) {
      updateProviderMutation.mutate({ 
        id: editingProvider.id, 
        updates: formData 
      });
    } else {
      createProviderMutation.mutate(formData);
    }
  };

  const handleEdit = (provider: LLMProviderConfig) => {
    setEditingProvider(provider);
    setFormData({
      provider: provider.provider,
      name: provider.name,
      base_url: provider.base_url,
      api_key: '', // Don't populate API key for security
      model: provider.model,
      connection_timeout: provider.connection_timeout,
      max_tokens: provider.max_tokens,
      temperature: provider.temperature,
    });
    setShowForm(true);
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingProvider(null);
    setFormData({
      provider: 'lmstudio',
      name: '',
      base_url: '',
      api_key: '',
      model: '',
      connection_timeout: 30,
      max_tokens: 8000,
      temperature: 0.7,
    });
  };

  const handleTestConnection = (id: number) => {
    setTestingProvider(id);
    testProviderMutation.mutate(id);
  };

  const handleUsePreset = (preset: LLMProviderPreset) => {
    setFormData({
      provider: preset.provider,
      name: preset.name,
      base_url: preset.base_url,
      api_key: '',
      model: preset.model,
      connection_timeout: 30,
      max_tokens: 8000,
      temperature: 0.7,
    });
    setShowForm(true);
  };

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case 'openai':
        return <CloudIcon className="h-5 w-5" />;
      case 'lmstudio':
        return <ComputerDesktopIcon className="h-5 w-5" />;
      default:
        return <BeakerIcon className="h-5 w-5" />;
    }
  };

  if (providersLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner size="md" message="Loading LLM providers..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            LLM Provider Configuration
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mt-1 text-sm">
            Configure and manage AI chat providers for runtime switching
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          disabled={showForm}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 text-sm font-medium transition-colors"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Provider
        </button>
      </div>

      {/* Active Provider Status */}
      {activeProvider && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <CheckCircleIcon className="h-5 w-5 text-green-500" />
            <div>
              <h4 className="text-sm font-medium text-green-800 dark:text-green-200">
                Active Provider: {activeProvider.name}
              </h4>
              <p className="text-xs text-green-600 dark:text-green-300">
                {activeProvider.provider.toUpperCase()} • {activeProvider.model} • {activeProvider.base_url}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Provider Form */}
      {showForm && (
        <div className="bg-white dark:bg-dark-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-medium text-gray-900 dark:text-white">
              {editingProvider ? 'Edit Provider' : 'Add New Provider'}
            </h4>
            <button
              onClick={handleCancel}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              Cancel
            </button>
          </div>

          {/* Preset Templates */}
          {!editingProvider && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Quick Setup from Template
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                {presets.map((preset) => (
                  <button
                    key={`${preset.provider}-${preset.name}`}
                    onClick={() => handleUsePreset(preset)}
                    className="flex items-center p-3 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-dark-700 text-left transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      {getProviderIcon(preset.provider)}
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {preset.name}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {preset.description}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Provider Type
                </label>
                <select
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value as 'openai' | 'lmstudio' | 'custom' })}
                  className="w-full px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="lmstudio">LMStudio</option>
                  <option value="openai">OpenAI</option>
                  <option value="custom">Custom</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Display Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="w-full px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="My LLM Provider"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Base URL *
                </label>
                <input
                  type="url"
                  value={formData.base_url}
                  onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
                  required
                  className="w-full px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="https://api.openai.com/v1"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  API Key {formData.provider !== 'lmstudio' && '*'}
                </label>
                <input
                  type="password"
                  value={formData.api_key}
                  onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                  required={formData.provider !== 'lmstudio'}
                  className="w-full px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder={formData.provider === 'lmstudio' ? 'Not required for LMStudio' : 'sk-...'}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Model *
                </label>
                <input
                  type="text"
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                  required
                  className="w-full px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="gpt-4"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Timeout (seconds)
                </label>
                <input
                  type="number"
                  value={formData.connection_timeout}
                  onChange={(e) => setFormData({ ...formData, connection_timeout: parseInt(e.target.value) })}
                  min="5"
                  max="300"
                  className="w-full px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Max Tokens
                </label>
                <input
                  type="number"
                  value={formData.max_tokens}
                  onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
                  min="1"
                  max="16000"
                  className="w-full px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="4000"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Maximum number of tokens to generate (1-16,000)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Temperature
                </label>
                <input
                  type="number"
                  value={formData.temperature}
                  onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
                  min="0"
                  max="2"
                  step="0.1"
                  className="w-full px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="0.7"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Controls randomness (0.0 = deterministic, 2.0 = very random)
                </p>
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={handleCancel}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createProviderMutation.isPending || updateProviderMutation.isPending}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
              >
                {createProviderMutation.isPending || updateProviderMutation.isPending 
                  ? 'Saving...' 
                  : editingProvider ? 'Update Provider' : 'Add Provider'
                }
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Provider List */}
      <div className="space-y-4">
        {providers.map((provider) => (
          <div
            key={provider.id}
            className={`bg-white dark:bg-dark-800 rounded-xl p-6 shadow-soft border transition-colors ${
              provider.is_active
                ? 'border-green-200 dark:border-green-700 bg-green-50/50 dark:bg-green-900/10'
                : 'border-gray-200 dark:border-gray-700'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  {getProviderIcon(provider.provider)}
                  <div>
                    <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                      {provider.name}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {provider.provider.toUpperCase()} • {provider.model}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      {provider.base_url}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {provider.is_active && (
                    <StatusBadge status="success" label="Active" size="sm" />
                  )}
                  {provider.is_default && (
                    <StatusBadge status="info" label="Default" size="sm" />
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleTestConnection(provider.id)}
                  disabled={testingProvider === provider.id}
                  className="px-3 py-1 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 transition-colors disabled:opacity-50"
                >
                  {testingProvider === provider.id ? 'Testing...' : 'Test'}
                </button>

                {!provider.is_active && (
                  <button
                    onClick={() => activateProviderMutation.mutate(provider.id)}
                    disabled={activateProviderMutation.isPending}
                    className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 transition-colors"
                  >
                    Activate
                  </button>
                )}

                <button
                  onClick={() => handleEdit(provider)}
                  className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                >
                  Edit
                </button>

                {!provider.is_active && (
                  <button
                    onClick={() => deleteProviderMutation.mutate(provider.id)}
                    disabled={deleteProviderMutation.isPending}
                    className="px-3 py-1 text-sm text-red-600 hover:text-red-800 transition-colors disabled:opacity-50"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}

        {providers.length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <BeakerIcon className="h-4 w-4 mx-auto mb-4 opacity-50" />
            <p>No LLM providers configured</p>
            <p className="text-sm">Add a provider to start using AI chat features</p>
          </div>
        )}
      </div>

      {/* Provider Settings Log */}
      {auditLogs.length > 0 && (
        <div className="bg-white dark:bg-dark-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
          <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            <ClockIcon className="h-5 w-5 mr-2" />
            Provider Settings Log
          </h4>
          <div className="space-y-3">
            {auditLogs.slice(0, 5).map((log) => (
              <div key={log.id} className="flex items-start space-x-3 text-sm">
                <div className="flex-shrink-0 mt-1">
                  {log.action === 'tested' ? (
                    <ExclamationTriangleIcon className="h-4 w-4 text-blue-500" />
                  ) : log.action === 'activated' ? (
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  ) : (
                    <div className="h-2 w-2 bg-gray-400 rounded-full mt-1" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-gray-900 dark:text-white">
                    Provider {log.action}
                    {log.test_result && log.test_result.success !== undefined && (
                      <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                        log.test_result.success 
                          ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400'
                          : 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-400'
                      }`}>
                        {log.test_result.success ? 'Success' : 'Failed'}
                      </span>
                    )}
                  </p>
                  <p className="text-gray-500 dark:text-gray-400 text-xs">
                    {new Date(log.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LLMProviderConfigSection;