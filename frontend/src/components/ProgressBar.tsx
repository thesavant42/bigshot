import React from 'react';

interface ProgressBarProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'error';
  showLabel?: boolean;
  label?: string;
  animated?: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  size = 'md',
  variant = 'default',
  showLabel = true,
  label,
  animated = false,
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  const getVariantClasses = () => {
    switch (variant) {
      case 'success':
        return 'bg-success-600';
      case 'warning':
        return 'bg-warning-600';
      case 'error':
        return 'bg-error-600';
      default:
        return 'bg-primary-600';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'h-2';
      case 'lg':
        return 'h-4';
      default:
        return 'h-3';
    }
  };

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {label || 'Progress'}
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {Math.round(percentage)}%
          </span>
        </div>
      )}
      
      <div className={`
        w-full bg-gray-200 dark:bg-dark-700 rounded-full overflow-hidden
        ${getSizeClasses()}
      `}>
        <div
          className={`
            h-full rounded-full transition-all duration-300 ease-out
            ${getVariantClasses()}
            ${animated ? 'animate-pulse' : ''}
          `}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
    </div>
  );
};

export default ProgressBar;