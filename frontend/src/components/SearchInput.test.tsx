import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SearchInput from './SearchInput';

describe('SearchInput', () => {
  it('renders with default props', () => {
    const onChange = vi.fn();
    render(<SearchInput value="" onChange={onChange} />);
    
    const input = screen.getByRole('searchbox');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('placeholder', 'Search...');
  });

  it('renders with custom placeholder', () => {
    const onChange = vi.fn();
    render(
      <SearchInput
        value=""
        onChange={onChange}
        placeholder="Search domains..."
      />
    );
    
    const input = screen.getByPlaceholderText('Search domains...');
    expect(input).toBeInTheDocument();
  });

  it('calls onChange when input value changes', () => {
    const onChange = vi.fn();
    render(<SearchInput value="" onChange={onChange} />);
    
    const input = screen.getByRole('searchbox');
    fireEvent.change(input, { target: { value: 'test' } });
    
    expect(onChange).toHaveBeenCalledWith('test');
  });

  it('shows keyboard shortcut when enabled', () => {
    const onChange = vi.fn();
    render(
      <SearchInput
        value=""
        onChange={onChange}
        showKeyboardShortcut={true}
        keyboardShortcut="Ctrl+K"
      />
    );
    
    expect(screen.getByText('Ctrl+K')).toBeInTheDocument();
  });

  it('applies header variant styling', () => {
    const onChange = vi.fn();
    render(
      <SearchInput
        value=""
        onChange={onChange}
        variant="header"
      />
    );
    
    const input = screen.getByRole('searchbox');
    expect(input).toHaveClass('bg-neutral-100', 'dark:bg-dark-700');
  });

  it('applies default variant styling', () => {
    const onChange = vi.fn();
    render(
      <SearchInput
        value=""
        onChange={onChange}
        variant="default"
      />
    );
    
    const input = screen.getByRole('searchbox');
    expect(input).toHaveClass('bg-gray-700');
  });
});