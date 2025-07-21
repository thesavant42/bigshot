import React, { useEffect, useState, useCallback } from 'react';
import { KeyboardContext, type KeyboardShortcut } from './KeyboardContextDefinition';

interface KeyboardProviderProps {
  children: React.ReactNode;
}

export const KeyboardProvider: React.FC<KeyboardProviderProps> = ({ children }) => {
  const [shortcuts, setShortcuts] = useState<KeyboardShortcut[]>([]);
  const [isHelpVisible, setIsHelpVisible] = useState(false);

  const addShortcut = useCallback((shortcut: KeyboardShortcut) => {
    setShortcuts(prev => [...prev.filter(s => s.key !== shortcut.key), shortcut]);
  }, []);

  const removeShortcut = useCallback((key: string) => {
    setShortcuts(prev => prev.filter(s => s.key !== key));
  }, []);

  const showHelp = useCallback(() => setIsHelpVisible(true), []);
  const hideHelp = useCallback(() => setIsHelpVisible(false), []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Show help on Ctrl+/ or Cmd+/
      if ((event.ctrlKey || event.metaKey) && event.key === '/') {
        event.preventDefault();
        showHelp();
        return;
      }

      // Hide help on Escape
      if (event.key === 'Escape' && isHelpVisible) {
        hideHelp();
        return;
      }

      // Find matching shortcut
      const matchedShortcut = shortcuts.find(shortcut => 
        shortcut.key === event.key &&
        !!shortcut.ctrlKey === event.ctrlKey &&
        !!shortcut.altKey === event.altKey &&
        !!shortcut.shiftKey === event.shiftKey &&
        !!shortcut.metaKey === event.metaKey
      );

      if (matchedShortcut) {
        event.preventDefault();
        matchedShortcut.callback();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts, isHelpVisible, showHelp, hideHelp]);

  // Add default shortcuts - only once on mount
  useEffect(() => {
    const defaultShortcuts: KeyboardShortcut[] = [
      {
        key: '/',
        ctrlKey: true,
        callback: showHelp,
        description: 'Show keyboard shortcuts',
      },
      {
        key: 'Escape',
        callback: hideHelp,
        description: 'Close modal/help',
      },
    ];

    // Directly set shortcuts without using addShortcut to avoid state change cycle
    setShortcuts(defaultShortcuts);
  }, []); // Empty dependency array - only run once on mount

  return (
    <KeyboardContext.Provider value={{
      shortcuts,
      addShortcut,
      removeShortcut,
      isHelpVisible,
      showHelp,
      hideHelp,
    }}>
      {children}
    </KeyboardContext.Provider>
  );
};