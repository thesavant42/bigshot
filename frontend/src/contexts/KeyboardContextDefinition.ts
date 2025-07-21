import { createContext } from 'react';

export interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  altKey?: boolean;
  shiftKey?: boolean;
  metaKey?: boolean;
  callback: () => void;
  description: string;
}

export interface KeyboardContextType {
  shortcuts: KeyboardShortcut[];
  addShortcut: (shortcut: KeyboardShortcut) => void;
  removeShortcut: (key: string) => void;
  isHelpVisible: boolean;
  showHelp: () => void;
  hideHelp: () => void;
}

export const KeyboardContext = createContext<KeyboardContextType | undefined>(undefined);