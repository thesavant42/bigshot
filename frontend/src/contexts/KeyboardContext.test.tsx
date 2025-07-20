import { describe, it, expect, vi } from 'vitest';
import { render, act } from '@testing-library/react';
import { KeyboardProvider } from './KeyboardContext';

// Mock the KeyboardContextDefinition to avoid circular dependencies  
vi.mock('./KeyboardContextDefinition', () => ({
  KeyboardContext: {
    Provider: ({ children }: { children: React.ReactNode }) => children
  }
}));

describe('KeyboardContext - Fixed infinite loop bug', () => {
  it('should not cause infinite re-renders', () => {
    let renderCount = 0;
    
    const TestComponent = () => {
      renderCount++;
      return <div>Test</div>;
    };

    // This test verifies that the useEffect with empty dependency array
    // prevents the infinite loop that was caused by including showHelp/hideHelp
    act(() => {
      render(
        <KeyboardProvider>
          <TestComponent />
        </KeyboardProvider>
      );
    });

    // In the fixed version, the TestComponent should render only once
    // This ensures that the infinite loop bug has been fixed
    expect(renderCount).toBe(1);
  });

  it('should initialize without throwing errors', () => {
    expect(() => {
      render(
        <KeyboardProvider>
          <div>Test child</div>
        </KeyboardProvider>
      );
    }).not.toThrow();
  });
});