import React from 'react';

interface QuickActionButtonsProps {
  onButtonClick: (message: string) => void;
  className?: string;
}

const quickActions = [
  {
    label: 'Recent discoveries',
    message: 'What domains have been discovered recently?'
  },
  {
    label: 'Domain hierarchy', 
    message: 'Show me the domain hierarchy for example.com'
  },
  {
    label: 'Start enumeration',
    message: 'Start enumeration for target.com'
  }
];

const QuickActionButtons: React.FC<QuickActionButtonsProps> = ({ 
  onButtonClick,
  className = ""
}) => {
  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {quickActions.map((action) => (
        <button
          key={action.label}
          onClick={() => onButtonClick(action.message)}
          className="px-3 py-1 bg-gray-700 text-gray-300 rounded-lg text-sm hover:bg-gray-600 transition-colors"
        >
          {action.label}
        </button>
      ))}
    </div>
  );
};

export default QuickActionButtons;