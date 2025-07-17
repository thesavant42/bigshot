import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
    >
      {theme === 'light' ? (
        <MoonIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
      ) : (
        <SunIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
      )}
    </button>
  );
};

export default ThemeToggle;