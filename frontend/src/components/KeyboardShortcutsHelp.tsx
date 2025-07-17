import React from 'react';
import { useKeyboard, type KeyboardShortcut } from '../hooks/useKeyboard';
import { XMarkIcon } from '@heroicons/react/24/outline';

const KeyboardShortcutsHelp: React.FC = () => {
  const { shortcuts, isHelpVisible, hideHelp } = useKeyboard();

  if (!isHelpVisible) return null;

  const formatShortcut = (shortcut: KeyboardShortcut) => {
    const keys = [];
    if (shortcut.ctrlKey) keys.push('Ctrl');
    if (shortcut.metaKey) keys.push('Cmd');
    if (shortcut.altKey) keys.push('Alt');
    if (shortcut.shiftKey) keys.push('Shift');
    keys.push(shortcut.key === ' ' ? 'Space' : shortcut.key);
    return keys.join(' + ');
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-dark-800 rounded-xl p-6 max-w-md w-full mx-4 shadow-strong">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Keyboard Shortcuts
          </h2>
          <button
            onClick={hideHelp}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            aria-label="Close shortcuts help"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>
        
        <div className="space-y-3">
          {shortcuts.map((shortcut, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {shortcut.description}
              </span>
              <kbd className="inline-flex items-center px-2 py-1 bg-gray-100 dark:bg-dark-700 text-gray-800 dark:text-gray-200 text-xs font-mono rounded">
                {formatShortcut(shortcut)}
              </kbd>
            </div>
          ))}
        </div>
        
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Press <kbd className="bg-gray-100 dark:bg-dark-700 px-1 py-0.5 rounded text-xs">Ctrl + /</kbd> to show this help
          </p>
        </div>
      </div>
    </div>
  );
};

export default KeyboardShortcutsHelp;