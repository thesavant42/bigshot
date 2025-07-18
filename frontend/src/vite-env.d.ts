/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly REACT_APP_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// TypeScript environment declarations for Node.js process.env
declare namespace NodeJS {
  interface ProcessEnv {
    readonly REACT_APP_API_URL?: string;
  }
}
