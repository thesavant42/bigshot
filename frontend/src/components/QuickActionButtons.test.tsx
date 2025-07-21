import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import QuickActionButtons from './QuickActionButtons';

describe('QuickActionButtons', () => {
  it('renders all quick action buttons', () => {
    const onButtonClick = vi.fn();
    render(<QuickActionButtons onButtonClick={onButtonClick} />);
    
    expect(screen.getByText('Recent discoveries')).toBeInTheDocument();
    expect(screen.getByText('Domain hierarchy')).toBeInTheDocument();
    expect(screen.getByText('Start enumeration')).toBeInTheDocument();
  });

  it('calls onButtonClick with correct message when button is clicked', () => {
    const onButtonClick = vi.fn();
    render(<QuickActionButtons onButtonClick={onButtonClick} />);
    
    fireEvent.click(screen.getByText('Recent discoveries'));
    expect(onButtonClick).toHaveBeenCalledWith('What domains have been discovered recently?');
    
    fireEvent.click(screen.getByText('Domain hierarchy'));
    expect(onButtonClick).toHaveBeenCalledWith('Show me the domain hierarchy for example.com');
    
    fireEvent.click(screen.getByText('Start enumeration'));
    expect(onButtonClick).toHaveBeenCalledWith('Start enumeration for target.com');
  });

  it('applies custom className', () => {
    const onButtonClick = vi.fn();
    const { container } = render(
      <QuickActionButtons 
        onButtonClick={onButtonClick} 
        className="custom-class"
      />
    );
    
    expect(container.firstChild).toHaveClass('custom-class');
  });
});