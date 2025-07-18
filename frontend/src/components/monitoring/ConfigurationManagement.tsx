import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CogIcon, ShieldCheckIcon, CircleStackIcon, ServerIcon, CloudIcon } from '@heroicons/react/24/outline';
import { apiService } from '../../services/api';
import LoadingSpinner from '../LoadingSpinner';
import StatusBadge from '../StatusBadge';

interface ConfigurationSection {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  settings: ConfigurationSetting[];
}

interface ConfigurationSetting {
  key: string;
  name: string;
  description: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'password';
  value: string | number | boolean;
  options?: string[];
  required?: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
  sensitive?: boolean;
}

const ConfigurationManagement: React.FC = () => {
  const [activeSection, setActiveSection] = useState('general');
  const [unsavedChanges, setUnsavedChanges] = useState<Record<string, string | number | boolean>>({});
  const queryClient = useQueryClient();

  const { isLoading } = useQuery({
    queryKey: ['config'],
    queryFn: () => apiService.getSettings(),
  });

  const updateConfigMutation = useMutation({
    mutationFn: ({ section, settings }: { section: string; settings: Record<string, string | number | boolean> }) =>
      apiService.updateSettings({ section, ...settings }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['config'] });
      setUnsavedChanges({});
    },
  });

  const exportConfigMutation = useMutation({
    mutationFn: () => apiService.getSettings(),
    onSuccess: (data) => {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `bigshot-config-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    },
  });

  const handleSettingChange = (sectionId: string, key: string, value: string | number | boolean) => {
    setUnsavedChanges(prev => ({
      ...prev,
      [`${sectionId}.${key}`]: value
    }));
  };

  const handleSaveSection = (sectionId: string) => {
    const sectionChanges = Object.entries(unsavedChanges)
      .filter(([key]) => key.startsWith(`${sectionId}.`))
      .reduce((acc, [key, value]) => {
        const settingKey = key.split('.').slice(1).join('.');
        acc[settingKey] = value;
        return acc;
      }, {} as Record<string, string | number | boolean>);

    if (Object.keys(sectionChanges).length > 0) {
      updateConfigMutation.mutate({ section: sectionId, settings: sectionChanges });
    }
  };

  const handleDiscardChanges = () => {
    setUnsavedChanges({});
  };

  const renderSettingInput = (section: ConfigurationSection, setting: ConfigurationSetting) => {
    const currentValue = unsavedChanges[`${section.id}.${setting.key}`] ?? setting.value;
    
    switch (setting.type) {
      case 'boolean': {
        // For boolean: ensure the type matches before assignment
        const boolValue: boolean | undefined = typeof currentValue === 'boolean' ? currentValue : undefined;
        return (
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={boolValue ?? false}
              onChange={(e) => handleSettingChange(section.id, setting.key, e.target.checked)}
              className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
          </div>
        );
      }
      
      case 'select': {
        // For select: ensure the value is string
        const stringValue: string | undefined = typeof currentValue === 'string' ? currentValue : undefined;
        return (
          <select
            value={stringValue ?? ''}
            onChange={(e) => handleSettingChange(section.id, setting.key, e.target.value)}
            className="w-full px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {setting.options?.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        );
      }
      
      case 'number': {
        // For number: ensure the value is number or convert string to number safely
        const numberValue: number | undefined = typeof currentValue === 'number' 
          ? currentValue 
          : typeof currentValue === 'string' && !isNaN(Number(currentValue))
          ? Number(currentValue)
          : undefined;
        return (
          <input
            type="number"
            value={numberValue ?? ''}
            onChange={(e) => handleSettingChange(section.id, setting.key, Number(e.target.value))}
            min={setting.validation?.min}
            max={setting.validation?.max}
            className="w-full px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        );
      }
      
      case 'password': {
        // For password: ensure the value is string  
        const passwordValue: string | undefined = typeof currentValue === 'string' ? currentValue : undefined;
        return (
          <input
            type="password"
            value={passwordValue ?? ''}
            onChange={(e) => handleSettingChange(section.id, setting.key, e.target.value)}
            className="w-full px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        );
      }
      
      default: {
        // For text: ensure the value is string
        const textValue: string | undefined = typeof currentValue === 'string' ? currentValue : undefined;
        return (
          <input
            type="text"
            value={textValue ?? ''}
            onChange={(e) => handleSettingChange(section.id, setting.key, e.target.value)}
            pattern={setting.validation?.pattern}
            className="w-full px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        );
      }
    }
  };

  // Mock configuration sections - in real app, this would come from the API
  const configSections: ConfigurationSection[] = [
    {
      id: 'general',
      name: 'General Settings',
      description: 'Basic application configuration',
      icon: CogIcon,
      settings: [
        {
          key: 'app_name',
          name: 'Application Name',
          description: 'Display name for the application',
          type: 'string',
          value: 'BigShot',
          required: true,
        },
        {
          key: 'debug_mode',
          name: 'Debug Mode',
          description: 'Enable debug logging and error details',
          type: 'boolean',
          value: false,
        },
        {
          key: 'max_concurrent_jobs',
          name: 'Max Concurrent Jobs',
          description: 'Maximum number of jobs that can run simultaneously',
          type: 'number',
          value: 4,
          validation: { min: 1, max: 16 },
        },
        {
          key: 'default_timeout',
          name: 'Default Timeout (seconds)',
          description: 'Default timeout for operations',
          type: 'number',
          value: 300,
          validation: { min: 60, max: 3600 },
        },
      ],
    },
    {
      id: 'security',
      name: 'Security Settings',
      description: 'Authentication and security configuration',
      icon: ShieldCheckIcon,
      settings: [
        {
          key: 'jwt_secret_key',
          name: 'JWT Secret Key',
          description: 'Secret key for JWT token generation',
          type: 'password',
          value: '********',
          required: true,
          sensitive: true,
        },
        {
          key: 'jwt_expiry_hours',
          name: 'JWT Expiry (hours)',
          description: 'JWT token expiration time in hours',
          type: 'number',
          value: 24,
          validation: { min: 1, max: 168 },
        },
        {
          key: 'rate_limit_enabled',
          name: 'Enable Rate Limiting',
          description: 'Enable API rate limiting',
          type: 'boolean',
          value: true,
        },
        {
          key: 'rate_limit_requests',
          name: 'Rate Limit Requests',
          description: 'Number of requests allowed per minute',
          type: 'number',
          value: 60,
          validation: { min: 10, max: 1000 },
        },
      ],
    },
    {
      id: 'database',
      name: 'Database Settings',
      description: 'Database connection and configuration',
      icon: CircleStackIcon,
      settings: [
        {
          key: 'database_url',
          name: 'Database URL',
          description: 'PostgreSQL connection string',
          type: 'string',
          value: 'postgresql://user:pass@localhost:5432/bigshot',
          required: true,
          sensitive: true,
        },
        {
          key: 'connection_pool_size',
          name: 'Connection Pool Size',
          description: 'Maximum number of database connections',
          type: 'number',
          value: 20,
          validation: { min: 5, max: 100 },
        },
        {
          key: 'query_timeout',
          name: 'Query Timeout (seconds)',
          description: 'Database query timeout',
          type: 'number',
          value: 30,
          validation: { min: 5, max: 300 },
        },
      ],
    },
    {
      id: 'redis',
      name: 'Redis Settings',
      description: 'Redis cache and message broker configuration',
      icon: ServerIcon,
      settings: [
        {
          key: 'redis_url',
          name: 'Redis URL',
          description: 'Redis connection string',
          type: 'string',
          value: 'redis://localhost:6379/0',
          required: true,
        },
        {
          key: 'redis_max_connections',
          name: 'Max Connections',
          description: 'Maximum Redis connections',
          type: 'number',
          value: 50,
          validation: { min: 10, max: 200 },
        },
        {
          key: 'cache_ttl',
          name: 'Cache TTL (seconds)',
          description: 'Default cache time-to-live',
          type: 'number',
          value: 3600,
          validation: { min: 60, max: 86400 },
        },
      ],
    },
    {
      id: 'integrations',
      name: 'External Integrations',
      description: 'Third-party service configurations',
      icon: CloudIcon,
      settings: [
        {
          key: 'openai_api_key',
          name: 'OpenAI API Key',
          description: 'API key for OpenAI services',
          type: 'password',
          value: '********',
          sensitive: true,
        },
        {
          key: 'openai_model',
          name: 'OpenAI Model',
          description: 'Default OpenAI model to use',
          type: 'select',
          value: 'gpt-4',
          options: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'],
        },
        {
          key: 'webhook_url',
          name: 'Webhook URL',
          description: 'URL for webhook notifications',
          type: 'string',
          value: '',
        },
        {
          key: 'enable_notifications',
          name: 'Enable Notifications',
          description: 'Enable webhook notifications',
          type: 'boolean',
          value: false,
        },
      ],
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="lg" message="Loading configuration..." />
      </div>
    );
  }

  const activeConfigSection = configSections.find(s => s.id === activeSection);
  const hasUnsavedChanges = Object.keys(unsavedChanges).length > 0;

  return (
    <div className="h-full overflow-hidden">
      <div className="flex h-full">
        {/* Sidebar */}
        <div className="w-64 bg-white dark:bg-dark-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
          <div className="p-6">
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">Configuration</h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Manage application settings
            </p>
          </div>
          
          <nav className="px-3 space-y-1">
            {configSections.map((section) => {
              const Icon = section.icon;
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                    activeSection === section.id
                      ? 'bg-primary-100 dark:bg-primary-900/20 text-primary-900 dark:text-primary-100'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700'
                  }`}
                >
                  <Icon className="h-5 w-5 mr-3" />
                  {section.name}
                </button>
              );
            })}
          </nav>

          <div className="p-3 mt-6 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={() => exportConfigMutation.mutate()}
              disabled={exportConfigMutation.isPending}
              className="w-full px-3 py-2 bg-gray-100 dark:bg-dark-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-dark-600 text-sm font-medium transition-colors disabled:opacity-50"
            >
              {exportConfigMutation.isPending ? 'Exporting...' : 'Export Config'}
            </button>
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1 overflow-y-auto">
          {activeConfigSection && (
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {activeConfigSection.name}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">
                    {activeConfigSection.description}
                  </p>
                </div>
                {hasUnsavedChanges && (
                  <div className="flex items-center space-x-3">
                    <StatusBadge
                      status="warning"
                      label="Unsaved changes"
                      size="sm"
                    />
                    <button
                      onClick={handleDiscardChanges}
                      className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
                    >
                      Discard
                    </button>
                    <button
                      onClick={() => handleSaveSection(activeSection)}
                      disabled={updateConfigMutation.isPending}
                      className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 text-sm font-medium transition-colors"
                    >
                      {updateConfigMutation.isPending ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                )}
              </div>

              {/* Settings */}
              <div className="space-y-6">
                {activeConfigSection.settings.map((setting) => (
                  <div key={setting.key} className="bg-white dark:bg-dark-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                            {setting.name}
                          </h3>
                          {setting.required && (
                            <span className="text-red-500 text-sm">*</span>
                          )}
                          {setting.sensitive && (
                            <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400 text-xs rounded-full">
                              Sensitive
                            </span>
                          )}
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 mt-1 text-sm">
                          {setting.description}
                        </p>
                      </div>
                      <div className="w-64 ml-6">
                        {renderSettingInput(activeConfigSection, setting)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConfigurationManagement;