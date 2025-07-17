import React from 'react';
import { CheckCircleIcon, XCircleIcon, ExclamationTriangleIcon, InformationCircleIcon } from '@heroicons/react/24/outline';

export type StatusType = 'success' | 'error' | 'warning' | 'info';

interface StatusBadgeProps {
  status: StatusType;
  label: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'solid' | 'outline' | 'soft';
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ 
  status, 
  label, 
  size = 'md', 
  variant = 'soft' 
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'success':
        return {
          icon: CheckCircleIcon,
          colors: {
            solid: 'bg-success-600 text-white',
            outline: 'border-success-600 text-success-600 bg-transparent',
            soft: 'bg-success-50 text-success-700 dark:bg-success-900/20 dark:text-success-400',
          },
        };
      case 'error':
        return {
          icon: XCircleIcon,
          colors: {
            solid: 'bg-error-600 text-white',
            outline: 'border-error-600 text-error-600 bg-transparent',
            soft: 'bg-error-50 text-error-700 dark:bg-error-900/20 dark:text-error-400',
          },
        };
      case 'warning':
        return {
          icon: ExclamationTriangleIcon,
          colors: {
            solid: 'bg-warning-600 text-white',
            outline: 'border-warning-600 text-warning-600 bg-transparent',
            soft: 'bg-warning-50 text-warning-700 dark:bg-warning-900/20 dark:text-warning-400',
          },
        };
      case 'info':
        return {
          icon: InformationCircleIcon,
          colors: {
            solid: 'bg-primary-600 text-white',
            outline: 'border-primary-600 text-primary-600 bg-transparent',
            soft: 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400',
          },
        };
      default:
        return {
          icon: InformationCircleIcon,
          colors: {
            solid: 'bg-gray-600 text-white',
            outline: 'border-gray-600 text-gray-600 bg-transparent',
            soft: 'bg-gray-50 text-gray-700 dark:bg-gray-900/20 dark:text-gray-400',
          },
        };
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-2 py-1 text-xs';
      case 'lg':
        return 'px-4 py-2 text-base';
      default:
        return 'px-3 py-1.5 text-sm';
    }
  };

  const getIconSize = () => {
    switch (size) {
      case 'sm':
        return 'h-3 w-3';
      case 'lg':
        return 'h-5 w-5';
      default:
        return 'h-4 w-4';
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <span 
      className={`
        inline-flex items-center gap-1.5 rounded-full font-medium
        ${getSizeClasses()}
        ${config.colors[variant]}
        ${variant === 'outline' ? 'border' : ''}
      `}
    >
      <Icon className={getIconSize()} />
      {label}
    </span>
  );
};

export default StatusBadge;