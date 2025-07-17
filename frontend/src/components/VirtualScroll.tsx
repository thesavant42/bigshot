import React, { useState, useEffect, useRef, useCallback } from 'react';

interface VirtualScrollItem<T = unknown> {
  id: string;
  height: number;
  data: T;
}

interface VirtualScrollProps<T = unknown> {
  items: VirtualScrollItem<T>[];
  itemHeight: number;
  containerHeight: number;
  overscan?: number;
  renderItem: (item: VirtualScrollItem<T>, index: number) => React.ReactNode;
  className?: string;
  onEndReached?: () => void;
  endReachedThreshold?: number;
}

const VirtualScroll = <T = unknown>({
  items,
  itemHeight,
  containerHeight,
  overscan = 5,
  renderItem,
  className = '',
  onEndReached,
  endReachedThreshold = 0.8,
}: VirtualScrollProps<T>) => {
  const [scrollTop, setScrollTop] = useState(0);
  const scrollElementRef = useRef<HTMLDivElement>(null);

  const totalHeight = items.length * itemHeight;
  const visibleItemsCount = Math.ceil(containerHeight / itemHeight);

  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    startIndex + visibleItemsCount + overscan * 2
  );

  const visibleItems = items.slice(startIndex, endIndex + 1);

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const scrollTop = e.currentTarget.scrollTop;
    setScrollTop(scrollTop);

    // Check if we've reached the end
    if (onEndReached && endReachedThreshold) {
      const { scrollHeight, clientHeight } = e.currentTarget;
      const scrollPercentage = (scrollTop + clientHeight) / scrollHeight;
      
      if (scrollPercentage >= endReachedThreshold) {
        onEndReached();
      }
    }
  }, [onEndReached, endReachedThreshold]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!scrollElementRef.current) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          scrollElementRef.current.scrollTop += itemHeight;
          break;
        case 'ArrowUp':
          e.preventDefault();
          scrollElementRef.current.scrollTop -= itemHeight;
          break;
        case 'PageDown':
          e.preventDefault();
          scrollElementRef.current.scrollTop += containerHeight;
          break;
        case 'PageUp':
          e.preventDefault();
          scrollElementRef.current.scrollTop -= containerHeight;
          break;
        case 'Home':
          e.preventDefault();
          scrollElementRef.current.scrollTop = 0;
          break;
        case 'End':
          e.preventDefault();
          scrollElementRef.current.scrollTop = totalHeight - containerHeight;
          break;
      }
    };

    const element = scrollElementRef.current;
    if (element) {
      element.addEventListener('keydown', handleKeyDown);
      return () => element.removeEventListener('keydown', handleKeyDown);
    }
  }, [itemHeight, containerHeight, totalHeight]);

  return (
    <div
      ref={scrollElementRef}
      className={`overflow-auto ${className}`}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
      tabIndex={0}
      role="grid"
      aria-label="Virtual scrollable list"
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${startIndex * itemHeight}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
          }}
        >
          {visibleItems.map((item, index) => (
            <div
              key={item.id}
              style={{ height: itemHeight }}
              role="gridcell"
              aria-rowindex={startIndex + index + 1}
            >
              {renderItem(item, startIndex + index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default VirtualScroll;