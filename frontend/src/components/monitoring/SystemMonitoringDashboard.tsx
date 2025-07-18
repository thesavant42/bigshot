import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChartBarIcon, CircleStackIcon, ServerIcon, CpuChipIcon } from '@heroicons/react/24/outline';
import { apiService } from '../../services/api';
import LoadingSpinner from '../LoadingSpinner';
import StatusBadge from '../StatusBadge';

interface SystemMetrics {
  system: {
    cpu_percent: number;
    memory_percent: number;
    memory_used_bytes: number;
    memory_total_bytes: number;
    disk_percent: number;
    disk_used_bytes: number;
    disk_total_bytes: number;
  };
  database: {
    domain_count: number;
    job_count: number;
    active_jobs: number;
  };
  redis: {
    memory_used_bytes: number;
    connected_clients: number;
  };
  websocket: {
    connected_clients: number;
  };
}

interface HealthStatus {
  status: string;
  timestamp: string;
  service: string;
  version: string;
  checks: {
    database: { status: string; error?: string };
    redis: { status: string; error?: string };
    celery: { status: string; error?: string; active_workers?: number };
    websocket: { status: string; error?: string; connected_clients?: number };
  };
}

interface SystemInfo {
  system: {
    platform: string;
    python_version: string;
    architecture: string;
  };
  environment: {
    flask_env: string;
    database_url: string;
    redis_url: string;
  };
}

interface BackupStatus {
  backups: Array<unknown>;
  total_size: number;
  last_backup: string | null;
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const MetricCard: React.FC<{
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ComponentType<{ className?: string }>;
  status?: 'success' | 'warning' | 'error';
  trend?: 'up' | 'down' | 'stable';
}> = ({ title, value, subtitle, icon: Icon, status, trend }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'success': return 'text-green-600 dark:text-green-400';
      case 'warning': return 'text-yellow-600 dark:text-yellow-400';
      case 'error': return 'text-red-600 dark:text-red-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  return (
    <div className="bg-white dark:bg-dark-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
            <Icon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</h3>
            <p className={`text-2xl font-bold ${getStatusColor()}`}>{value}</p>
            {subtitle && <p className="text-xs text-gray-500 dark:text-gray-500">{subtitle}</p>}
          </div>
        </div>
        {trend && (
          <div className={`text-sm font-medium ${
            trend === 'up' ? 'text-green-600 dark:text-green-400' :
            trend === 'down' ? 'text-red-600 dark:text-red-400' :
            'text-gray-600 dark:text-gray-400'
          }`}>
            {trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→'}
          </div>
        )}
      </div>
    </div>
  );
};

const ProgressBar: React.FC<{
  value: number;
  max: number;
  label: string;
  color?: 'primary' | 'success' | 'warning' | 'error';
}> = ({ value, max, label, color = 'primary' }) => {
  const percentage = (value / max) * 100;
  
  const getColorClasses = () => {
    switch (color) {
      case 'success': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-primary-500';
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-gray-600 dark:text-gray-400">{label}</span>
        <span className="text-gray-900 dark:text-white font-medium">{percentage.toFixed(1)}%</span>
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${getColorClasses()}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

const SystemMonitoringDashboard: React.FC = () => {
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds

  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['health', 'detailed'],
    queryFn: () => apiService.get<HealthStatus>('/health/detailed'),
    refetchInterval: refreshInterval,
  });

  const { data: metricsData, isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: () => apiService.get<SystemMetrics>('/metrics'),
    refetchInterval: refreshInterval,
  });

  const { data: systemInfo } = useQuery({
    queryKey: ['system', 'info'],
    queryFn: () => apiService.get<SystemInfo>('/system/info'),
    refetchInterval: 300000, // 5 minutes
  });

  const { data: backupStatus } = useQuery({
    queryKey: ['backup', 'status'],
    queryFn: () => apiService.get<BackupStatus>('/backup/status'),
    refetchInterval: 300000, // 5 minutes
  });

  if (healthLoading || metricsLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="lg" message="Loading system metrics..." />
      </div>
    );
  }

  const getHealthStatus = (status: string) => {
    switch (status) {
      case 'healthy': return 'success';
      case 'degraded': return 'warning';
      case 'unhealthy': return 'error';
      default: return 'error';
    }
  };

  const getPercentageStatus = (percentage: number) => {
    if (percentage > 90) return 'error';
    if (percentage > 70) return 'warning';
    return 'success';
  };

  return (
    <div className="h-full overflow-auto">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">System Monitoring</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Real-time system health and performance metrics
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="px-3 py-2 bg-white dark:bg-dark-700 border border-gray-300 dark:border-gray-600 rounded-lg text-sm"
            >
              <option value={10000}>10s</option>
              <option value={30000}>30s</option>
              <option value={60000}>1m</option>
              <option value={300000}>5m</option>
            </select>
            <StatusBadge
              status={healthData ? getHealthStatus(healthData.status) : 'error'}
              label={healthData?.status || 'Unknown'}
            />
          </div>
        </div>

        {/* System Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="CPU Usage"
            value={`${metricsData?.system.cpu_percent.toFixed(1)}%`}
            icon={CpuChipIcon}
            status={getPercentageStatus(metricsData?.system.cpu_percent || 0)}
          />
          <MetricCard
            title="Memory Usage"
            value={`${metricsData?.system.memory_percent.toFixed(1)}%`}
            subtitle={`${formatBytes(metricsData?.system.memory_used_bytes || 0)} / ${formatBytes(metricsData?.system.memory_total_bytes || 0)}`}
            icon={ServerIcon}
            status={getPercentageStatus(metricsData?.system.memory_percent || 0)}
          />
          <MetricCard
            title="Disk Usage"
            value={`${metricsData?.system.disk_percent.toFixed(1)}%`}
            subtitle={`${formatBytes(metricsData?.system.disk_used_bytes || 0)} / ${formatBytes(metricsData?.system.disk_total_bytes || 0)}`}
            icon={CircleStackIcon}
            status={getPercentageStatus(metricsData?.system.disk_percent || 0)}
          />
          <MetricCard
            title="Active Jobs"
            value={metricsData?.database.active_jobs || 0}
            subtitle={`${metricsData?.database.job_count || 0} total jobs`}
            icon={ChartBarIcon}
          />
        </div>

        {/* Service Status */}
        <div className="bg-white dark:bg-dark-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Service Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {healthData?.checks && Object.entries(healthData.checks).map(([service, check]) => (
              <div key={service} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900 dark:text-white capitalize">{service}</p>
                  {check.error && (
                    <p className="text-xs text-red-600 dark:text-red-400 mt-1">{check.error}</p>
                  )}
                </div>
                <StatusBadge
                  status={check.status === 'healthy' ? 'success' : 'error'}
                  label={check.status}
                  size="sm"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Resource Usage */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-dark-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Resource Usage</h2>
            <div className="space-y-4">
              <ProgressBar
                value={metricsData?.system.cpu_percent || 0}
                max={100}
                label="CPU"
                color={getPercentageStatus(metricsData?.system.cpu_percent || 0)}
              />
              <ProgressBar
                value={metricsData?.system.memory_percent || 0}
                max={100}
                label="Memory"
                color={getPercentageStatus(metricsData?.system.memory_percent || 0)}
              />
              <ProgressBar
                value={metricsData?.system.disk_percent || 0}
                max={100}
                label="Disk"
                color={getPercentageStatus(metricsData?.system.disk_percent || 0)}
              />
            </div>
          </div>

          <div className="bg-white dark:bg-dark-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Database & Cache</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <span className="text-gray-600 dark:text-gray-400">Domains</span>
                <span className="font-medium text-gray-900 dark:text-white">{metricsData?.database.domain_count || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <span className="text-gray-600 dark:text-gray-400">Total Jobs</span>
                <span className="font-medium text-gray-900 dark:text-white">{metricsData?.database.job_count || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <span className="text-gray-600 dark:text-gray-400">Redis Memory</span>
                <span className="font-medium text-gray-900 dark:text-white">{formatBytes(metricsData?.redis.memory_used_bytes || 0)}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <span className="text-gray-600 dark:text-gray-400">WebSocket Clients</span>
                <span className="font-medium text-gray-900 dark:text-white">{metricsData?.websocket.connected_clients || 0}</span>
              </div>
            </div>
          </div>
        </div>

        {/* System Information */}
        {systemInfo && (
          <div className="bg-white dark:bg-dark-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">System Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">System</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Platform:</span>
                    <span className="text-gray-900 dark:text-white">{systemInfo?.system?.platform || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Python:</span>
                    <span className="text-gray-900 dark:text-white">{systemInfo?.system?.python_version || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Architecture:</span>
                    <span className="text-gray-900 dark:text-white">{systemInfo?.system?.architecture || 'N/A'}</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Environment</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Flask Environment:</span>
                    <span className="text-gray-900 dark:text-white">{systemInfo?.environment?.flask_env || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Database:</span>
                    <span className="text-gray-900 dark:text-white">{systemInfo?.environment?.database_url || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Redis:</span>
                    <span className="text-gray-900 dark:text-white">{systemInfo?.environment?.redis_url || 'N/A'}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Backup Status */}
        {backupStatus && (
          <div className="bg-white dark:bg-dark-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Backup Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <span className="text-gray-600 dark:text-gray-400">Total Backups</span>
                <span className="font-medium text-gray-900 dark:text-white">{backupStatus?.backups?.length || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <span className="text-gray-600 dark:text-gray-400">Total Size</span>
                <span className="font-medium text-gray-900 dark:text-white">{formatBytes(backupStatus?.total_size || 0)}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <span className="text-gray-600 dark:text-gray-400">Last Backup</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {backupStatus?.last_backup ? new Date(backupStatus.last_backup).toLocaleDateString() : 'None'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemMonitoringDashboard;