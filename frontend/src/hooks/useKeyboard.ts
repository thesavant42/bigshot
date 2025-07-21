import { useContext } from 'react';
import { KeyboardContext, type KeyboardContextType } from '../contexts/KeyboardContextDefinition';

export const useKeyboard = (): KeyboardContextType => {
  const context = useContext(KeyboardContext);
  if (!context) {
    throw new Error('useKeyboard must be used within a KeyboardProvider');
  }
  return context;
};