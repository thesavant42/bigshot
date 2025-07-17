import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'primary' | 'secondary' | 'white';
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  variant = 'primary',
  message,
}) => {
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'h-4 w-4';
      case 'lg':
        return 'h-8 w-8';
      case 'xl':
        return 'h-12 w-12';
      default:
        return 'h-6 w-6';
    }
  };

  const getVariantClasses = () => {
    switch (variant) {
      case 'secondary':
        return 'border-gray-300 border-t-gray-600';
      case 'white':
        return 'border-white/20 border-t-white';
      default:
        return 'border-gray-200 dark:border-gray-700 border-t-primary-600';
    }
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div
        className={`
          animate-spin rounded-full border-2
          ${getSizeClasses()}
          ${getVariantClasses()}
        `}
        role="status"
        aria-label={message || 'Loading'}
      />
      {message && (
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {message}
        </p>
      )}
    </div>
  );
};

export default LoadingSpinner;