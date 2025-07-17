import React, { createContext, useContext, useEffect, useState } from 'react';

interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  altKey?: boolean;
  shiftKey?: boolean;
  metaKey?: boolean;
  callback: () => void;
  description: string;
}

interface KeyboardContextType {
  shortcuts: KeyboardShortcut[];
  addShortcut: (shortcut: KeyboardShortcut) => void;
  removeShortcut: (key: string) => void;
  isHelpVisible: boolean;
  showHelp: () => void;
  hideHelp: () => void;
}

const KeyboardContext = createContext<KeyboardContextType | undefined>(undefined);

export const useKeyboard = (): KeyboardContextType => {
  const context = useContext(KeyboardContext);
  if (!context) {
    throw new Error('useKeyboard must be used within a KeyboardProvider');
  }
  return context;
};

interface KeyboardProviderProps {
  children: React.ReactNode;
}

export const KeyboardProvider: React.FC<KeyboardProviderProps> = ({ children }) => {
  const [shortcuts, setShortcuts] = useState<KeyboardShortcut[]>([]);
  const [isHelpVisible, setIsHelpVisible] = useState(false);

  const addShortcut = (shortcut: KeyboardShortcut) => {
    setShortcuts(prev => [...prev.filter(s => s.key !== shortcut.key), shortcut]);
  };

  const removeShortcut = (key: string) => {
    setShortcuts(prev => prev.filter(s => s.key !== key));
  };

  const showHelp = () => setIsHelpVisible(true);
  const hideHelp = () => setIsHelpVisible(false);

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
  }, [shortcuts, isHelpVisible]);

  // Add default shortcuts
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

    defaultShortcuts.forEach(addShortcut);
  }, []);

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