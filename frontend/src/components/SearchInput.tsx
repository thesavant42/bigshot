import React from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  showKeyboardShortcut?: boolean;
  keyboardShortcut?: string;
  id?: string;
  variant?: 'default' | 'header';
}

const SearchInput: React.FC<SearchInputProps> = ({
  value,
  onChange,
  placeholder = "Search...",
  className = "",
  showKeyboardShortcut = false,
  keyboardShortcut = "Ctrl+K",
  id,
  variant = 'default'
}) => {
  const inputStyles = variant === 'header' 
    ? "w-full pl-10 pr-16 py-2 bg-neutral-100 dark:bg-dark-700 border border-neutral-300 dark:border-dark-600 text-neutral-900 dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 placeholder-neutral-500 dark:placeholder-neutral-400 transition-colors"
    : "w-full pl-10 pr-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400 transition-colors";

  const iconStyles = variant === 'header' 
    ? "h-5 w-5 text-neutral-400"
    : "h-5 w-5 text-gray-400";

  const kbdStyles = variant === 'header'
    ? "hidden sm:inline-flex items-center px-2 py-1 bg-neutral-200 dark:bg-dark-600 text-neutral-600 dark:text-neutral-400 text-xs rounded"
    : "hidden sm:inline-flex items-center px-2 py-1 bg-gray-600 text-gray-400 text-xs rounded";

  return (
    <div className={`relative ${className}`}>
      <input
        id={id}
        type="search"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={inputStyles}
      />
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <MagnifyingGlassIcon className={iconStyles} />
      </div>
      {showKeyboardShortcut && (
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <kbd className={kbdStyles}>
            {keyboardShortcut}
          </kbd>
        </div>
      )}
    </div>
  );
};

export default SearchInput;