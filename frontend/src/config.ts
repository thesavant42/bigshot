interface GlobalWithEnv {
  process?: {
    env?: {
      REACT_APP_API_URL?: string;
    };
  };
}

const globalWithEnv = globalThis as unknown as GlobalWithEnv;
export const API_BASE_URL =
  globalWithEnv.process?.env?.REACT_APP_API_URL || 'http://localhost:5000';