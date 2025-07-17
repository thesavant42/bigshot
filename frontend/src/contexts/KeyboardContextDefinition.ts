import { createContext } from 'react';
import type { KeyboardContextType } from '../hooks/useKeyboard';

export const KeyboardContext = createContext<KeyboardContextType | undefined>(undefined);