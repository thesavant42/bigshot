/// <reference types="vitest" />
import { defineConfig } from 'vitest/config'

// https://vitest.dev/config/
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
    // Exclude E2E tests from Vitest - they should only run with Playwright
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/tests/e2e/**',
      '**/*.e2e.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        'dist/',
        'build/',
        'tests/e2e/',
        '**/*.d.ts',
        '**/*.config.js',
        '**/*.config.ts',
      ],
    },
  },
})