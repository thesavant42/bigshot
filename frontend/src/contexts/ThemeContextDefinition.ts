import { createContext } from 'react';
import type { ThemeContextType } from '../hooks/useTheme';

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);