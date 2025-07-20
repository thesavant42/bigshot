import React from 'react';
import { XMarkIcon, PlayIcon, StopIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import { useJobs } from '../../hooks/useApi';
import type { Job } from '../../types';

interface JobStatusPanelProps {
  onClose: () => void;
}

const JobStatusPanel: React.FC<JobStatusPanelProps> = ({ onClose }) => {
  const { jobs, isLoading, cancelJob } = useJobs();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <PlayIcon className="h-5 w-5 text-yellow-500" />;
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'cancelled':
        return <StopIcon className="h-5 w-5 text-gray-500" />;
      default:
        return <div className="h-5 w-5 rounded-full bg-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'text-yellow-400';
      case 'completed':
        return 'text-green-400';
      case 'failed':
        return 'text-red-400';
      case 'cancelled':
        return 'text-gray-400';
      default:
        return 'text-gray-400';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      await cancelJob.mutateAsync(jobId);
    } catch (error) {
      console.error('Failed to cancel job:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[80vh] overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Job Status</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="overflow-y-auto max-h-[60vh]">
            {jobs && jobs.length > 0 ? (
              <div className="space-y-4">
                {jobs.map((job: Job) => (
                  <div
                    key={job.id}
                    className="bg-gray-700 rounded-lg p-4 border border-gray-600"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(job.status)}
                        <div>
                          <div className="font-medium text-white">
                            {job.type} - {job.target_domains?.join(', ') || 'No domains'}
                          </div>
                          <div className="text-sm text-gray-400">
                            Sources: {job.sources?.join(', ') || 'No sources'}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div className={`font-medium ${getStatusColor(job.status)}`}>
                            {job.status.toUpperCase()}
                          </div>
                          <div className="text-sm text-gray-400">
                            {job.results_count !== undefined && `${job.results_count} results`}
                          </div>
                        </div>
                        {job.status === 'running' && (
                          <button
                            onClick={() => handleCancelJob(job.id)}
                            className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                          >
                            Cancel
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Progress Bar */}
                    {job.status === 'running' && job.progress !== undefined && (
                      <div className="mt-3">
                        <div className="flex justify-between text-sm text-gray-400 mb-1">
                          <span>Progress</span>
                          <span>{job.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-600 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${job.progress}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {/* Job Details */}
                    <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Started:</span>
                        <span className="text-white ml-2">{formatDate(job.created_at)}</span>
                      </div>
                      {job.completed_at && (
                        <div>
                          <span className="text-gray-400">Completed:</span>
                          <span className="text-white ml-2">{formatDate(job.completed_at)}</span>
                        </div>
                      )}
                    </div>

                    {/* Error Message */}
                    {job.error && (
                      <div className="mt-3 p-3 bg-red-900 bg-opacity-50 border border-red-700 rounded">
                        <div className="text-sm text-red-300">
                          Error: {job.error}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                No jobs found
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default JobStatusPanel;