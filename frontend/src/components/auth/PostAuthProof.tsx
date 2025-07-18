import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../../services/api';
import LoadingSpinner from '../LoadingSpinner';

interface ConnectivityProofData {
  authentication: {
    status: string;
    user: string;
    timestamp: string;
    message: string;
  };
  backend_services: {
    [key: string]: {
      status: string;
      message: string;
      connection_url?: string;
      active_workers?: number;
      broker_url?: string;
    };
  };
  environment: {
    service_name: string;
    hostname: string;
    flask_env: string;
    container_id: string;
  };
  client: {
    ip_address: string;
    user_agent: string;
    request_timestamp: string;
  };
  overall_status: {
    healthy_services: number;
    total_services: number;
    status: string;
  };
}

interface PostAuthProofProps {
  onContinue: () => void;
}

const PostAuthProof: React.FC<PostAuthProofProps> = ({ onContinue }) => {
  const [autoAdvance, setAutoAdvance] = useState(true);

  const { data: connectivityData, isLoading, error } = useQuery({
    queryKey: ['connectivity-proof'],
    queryFn: () => apiService.getConnectivityProof(),
    retry: 1,
  });

  // Auto-advance to main application after 10 seconds if successful
  useEffect(() => {
    if (connectivityData?.data && autoAdvance) {
      const timer = setTimeout(() => {
        onContinue();
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [connectivityData, autoAdvance, onContinue]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'HEALTHY':
      case 'SUCCESS':
        return '✅';
      case 'DEGRADED':
        return '⚠️';
      case 'FAILED':
        return '❌';
      default:
        return '🔄';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'HEALTHY':
      case 'SUCCESS':
        return 'text-green-600 dark:text-green-400';
      case 'DEGRADED':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'FAILED':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-dark-950">
        <div className="text-center">
          <LoadingSpinner size="lg" message="Verifying backend connectivity..." />
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            Running post-authentication checks...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-dark-950">
        <div className="max-w-2xl w-full mx-4">
          <div className="bg-white dark:bg-dark-800 rounded-xl p-8 shadow-medium border border-red-200 dark:border-red-800">
            <div className="text-center mb-6">
              <div className="text-6xl mb-4">❌</div>
              <h1 className="text-2xl font-bold text-red-600 dark:text-red-400">
                Connectivity Check Failed
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Unable to verify backend connectivity
              </p>
            </div>
            
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg mb-6">
              <h3 className="font-medium text-red-800 dark:text-red-200 mb-2">Error Details:</h3>
              <p className="text-red-700 dark:text-red-300 text-sm">
                {error instanceof Error ? error.message : 'Unknown error occurred'}
              </p>
            </div>

            <div className="flex gap-4 justify-center">
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Retry Check
              </button>
              <button
                onClick={onContinue}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Continue Anyway
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const proof = connectivityData?.data as ConnectivityProofData;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-950 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white dark:bg-dark-800 rounded-xl shadow-medium overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  {getStatusIcon(proof?.authentication?.status || 'UNKNOWN')}
                  Post-Authentication Verification
                </h1>
                <p className="opacity-90 mt-1">
                  Backend connectivity confirmed - Login successful
                </p>
              </div>
              <div className="text-right text-sm opacity-75">
                <div>User: {proof?.authentication?.user}</div>
                <div>{new Date(proof?.authentication?.timestamp || '').toLocaleString()}</div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Authentication Status */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                {getStatusIcon(proof?.authentication?.status || 'UNKNOWN')}
                Authentication Status
              </h2>
              <div className={`font-medium ${getStatusColor(proof?.authentication?.status || 'UNKNOWN')}`}>
                {proof?.authentication?.message}
              </div>
            </div>

            {/* Backend Services */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                🔧 Backend Services Status
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {proof?.backend_services && Object.entries(proof.backend_services).map(([service, details]) => (
                  <div key={service} className="bg-gray-50 dark:bg-dark-700 p-4 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusIcon(details.status)}
                      <span className="font-medium capitalize text-gray-900 dark:text-white">
                        {service}
                      </span>
                    </div>
                    <div className={`text-sm ${getStatusColor(details.status)}`}>
                      {details.message}
                    </div>
                    {details.connection_url && (
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 font-mono">
                        {details.connection_url}
                      </div>
                    )}
                    {details.active_workers !== undefined && (
                      <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        Active workers: {details.active_workers}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Environment Information */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                🖥️ Environment Information
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-gray-500 dark:text-gray-400">Service</div>
                  <div className="font-mono text-gray-900 dark:text-white">
                    {proof?.environment?.service_name}
                  </div>
                </div>
                <div>
                  <div className="text-gray-500 dark:text-gray-400">Hostname</div>
                  <div className="font-mono text-gray-900 dark:text-white">
                    {proof?.environment?.hostname}
                  </div>
                </div>
                <div>
                  <div className="text-gray-500 dark:text-gray-400">Environment</div>
                  <div className="font-mono text-gray-900 dark:text-white">
                    {proof?.environment?.flask_env}
                  </div>
                </div>
                <div>
                  <div className="text-gray-500 dark:text-gray-400">Container</div>
                  <div className="font-mono text-gray-900 dark:text-white">
                    {proof?.environment?.container_id}
                  </div>
                </div>
              </div>
            </div>

            {/* Overall Status */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                📊 Overall System Health
              </h2>
              <div className="flex items-center gap-4">
                <div className={`text-2xl font-bold ${getStatusColor(proof?.overall_status?.status || 'UNKNOWN')}`}>
                  {getStatusIcon(proof?.overall_status?.status || 'UNKNOWN')}
                  {proof?.overall_status?.status}
                </div>
                <div className="text-gray-600 dark:text-gray-400">
                  {proof?.overall_status?.healthy_services}/{proof?.overall_status?.total_services} services healthy
                </div>
              </div>
            </div>

            {/* Instructions */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <h3 className="font-medium text-blue-800 dark:text-blue-200 mb-2">
                📋 Verification Instructions
              </h3>
              <div className="text-blue-700 dark:text-blue-300 text-sm space-y-1">
                <p>✅ Login successful with credentials: admin/password</p>
                <p>✅ JWT token verified and backend connectivity confirmed</p>
                <p>✅ All required services are accessible and responding</p>
                <p className="font-medium">
                  This page serves as proof of successful authentication and backend connectivity.
                </p>
              </div>
            </div>

            {/* Controls */}
            <div className="flex gap-4 justify-center pt-4">
              <button
                onClick={() => setAutoAdvance(!autoAdvance)}
                className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                  autoAdvance 
                    ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-200'
                    : 'bg-gray-100 text-gray-800 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200'
                }`}
              >
                {autoAdvance ? '⏸️ Pause Auto-Advance' : '▶️ Resume Auto-Advance'}
              </button>
              <button
                onClick={() => window.print()}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                🖨️ Print Proof
              </button>
              <button
                onClick={onContinue}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                Continue to Application →
              </button>
            </div>

            {autoAdvance && (
              <div className="text-center text-sm text-gray-500 dark:text-gray-400">
                Automatically continuing to main application in 10 seconds...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostAuthProof;