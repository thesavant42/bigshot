/// <reference types="vitest" />
import { defineConfig } from 'vitest/config'

// https://vitest.dev/config/
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/tests/e2e/**', // Exclude Playwright E2E tests
      '**/*.spec.ts', // Exclude Playwright spec files
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        'dist/',
        'build/',
        '**/*.d.ts',
        '**/*.config.js',
        '**/*.config.ts',
      ],
    },
  },
})