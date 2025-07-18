// TypeScript interface for properly typing globalThis environment access
export interface GlobalWithEnv {
  process?: {
    env?: {
      REACT_APP_API_URL?: string;
    };
  };
}