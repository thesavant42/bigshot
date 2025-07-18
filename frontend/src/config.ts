import type { GlobalWithEnv } from './types/global';

const globalWithEnv = globalThis as GlobalWithEnv;
export const API_BASE_URL =
  globalWithEnv.process?.env?.REACT_APP_API_URL || 'http://localhost:5000';