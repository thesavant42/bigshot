# BigShot Design Guidelines

## Overview

This document outlines the design system and guidelines for the BigShot domain reconnaissance platform. The design follows modern FANG-style principles with a focus on accessibility, performance, and user experience.

## Design Principles

### 1. Accessibility First
- **WCAG 2.1 AA Compliance**: All components meet or exceed WCAG 2.1 AA standards
- **Keyboard Navigation**: Full keyboard support with visible focus indicators
- **Screen Reader Support**: Proper ARIA labels and semantic HTML
- **Color Contrast**: Minimum 4.5:1 contrast ratio for normal text, 3:1 for large text

### 2. Performance Oriented
- **Virtual Scrolling**: Large datasets use virtual scrolling for optimal performance
- **Lazy Loading**: Images and components load on-demand
- **Minimal Bundle Size**: Tree-shaking and code splitting implemented
- **Progressive Enhancement**: Core functionality works without JavaScript

### 3. Responsive Design
- **Mobile-First**: Designed for mobile devices first, then enhanced for larger screens
- **Fluid Typography**: Text scales appropriately across devices
- **Touch-Friendly**: Minimum 44px touch targets
- **Flexible Layouts**: Uses CSS Grid and Flexbox for responsive layouts

## Color Palette

### Primary Colors
- **Primary 50**: `#eff6ff` - Light background, subtle accents
- **Primary 500**: `#3b82f6` - Main brand color, CTAs
- **Primary 600**: `#2563eb` - Hover states, active elements
- **Primary 900**: `#1e3a8a` - Dark text, high contrast

### Secondary Colors
- **Secondary 100**: `#f1f5f9` - Light backgrounds
- **Secondary 500**: `#64748b` - Body text, secondary elements
- **Secondary 800**: `#1e293b` - Dark backgrounds, headings
- **Secondary 950**: `#020617` - Darkest backgrounds

### Status Colors
- **Success**: `#22c55e` - Success states, positive feedback
- **Warning**: `#f59e0b` - Warning states, attention needed
- **Error**: `#ef4444` - Error states, destructive actions
- **Info**: `#3b82f6` - Information, neutral feedback

### Dark Theme Colors
- **Dark 50**: `#f8fafc` - Light text on dark backgrounds
- **Dark 700**: `#334155` - Medium dark backgrounds
- **Dark 800**: `#1e293b` - Dark backgrounds
- **Dark 950**: `#020617` - Darkest backgrounds

## Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

### Font Sizes
- **Text XS**: `0.75rem` (12px) - Captions, helper text
- **Text SM**: `0.875rem` (14px) - Body text, labels
- **Text Base**: `1rem` (16px) - Default body text
- **Text LG**: `1.125rem` (18px) - Subheadings
- **Text XL**: `1.25rem` (20px) - Headings
- **Text 2XL**: `1.5rem` (24px) - Page titles
- **Text 3XL**: `1.875rem` (30px) - Hero titles

### Font Weights
- **Light**: 300 - Subtle text
- **Normal**: 400 - Body text
- **Medium**: 500 - Emphasis
- **Semibold**: 600 - Headings
- **Bold**: 700 - Strong emphasis

## Spacing

### Spacing Scale
- **1**: `0.25rem` (4px)
- **2**: `0.5rem` (8px)
- **3**: `0.75rem` (12px)
- **4**: `1rem` (16px)
- **6**: `1.5rem` (24px)
- **8**: `2rem` (32px)
- **12**: `3rem` (48px)
- **16**: `4rem` (64px)

### Component Spacing
- **Button Padding**: `px-4 py-2` (16px horizontal, 8px vertical)
- **Card Padding**: `p-6` (24px all sides)
- **Section Spacing**: `space-y-8` (32px vertical)

## Components

### Buttons
- **Primary**: Blue background, white text
- **Secondary**: Gray outline, gray text
- **Ghost**: Transparent background, colored text
- **Minimum Size**: 44px height for touch targets
- **Focus Ring**: 2px primary color ring with 2px offset

### Cards
- **Background**: White in light mode, dark-800 in dark mode
- **Border**: 1px solid gray-200 in light mode, gray-700 in dark mode
- **Border Radius**: 8px
- **Shadow**: Soft shadow for elevation
- **Padding**: 24px

### Form Elements
- **Input Height**: 40px minimum
- **Border**: 1px solid gray-300, primary-500 on focus
- **Border Radius**: 6px
- **Padding**: 12px horizontal, 8px vertical
- **Placeholder**: gray-500 color

### Status Indicators
- **Success**: Green background, check icon
- **Warning**: Yellow background, exclamation icon
- **Error**: Red background, X icon
- **Info**: Blue background, info icon

## Layout

### Grid System
- **Container**: Max-width with centered content
- **Breakpoints**: 
  - `sm`: 640px
  - `md`: 768px
  - `lg`: 1024px
  - `xl`: 1280px
  - `2xl`: 1536px

### Sidebar
- **Width**: 256px (desktop)
- **Collapsible**: Mobile-first collapsible navigation
- **Background**: White/dark-800 with border

### Header
- **Height**: 64px
- **Background**: White/dark-800 with bottom border
- **Elements**: Logo, navigation, user menu, theme toggle

## Accessibility

### Focus Management
- **Focus Indicators**: Visible 2px ring around focusable elements
- **Focus Trap**: Modals and dropdowns trap focus
- **Skip Links**: Hidden skip-to-content links for screen readers

### ARIA Labels
- **Interactive Elements**: All buttons, links, and form elements have labels
- **Status Updates**: Dynamic content changes announced to screen readers
- **Landmarks**: Proper use of nav, main, aside, and other landmarks

### Color Contrast
- **Normal Text**: 4.5:1 minimum contrast ratio
- **Large Text**: 3:1 minimum contrast ratio
- **Interactive Elements**: 3:1 minimum contrast ratio
- **Focus Indicators**: 3:1 minimum contrast ratio

## Animation

### Timing Functions
- **Ease-Out**: For elements entering the screen
- **Ease-In**: For elements leaving the screen
- **Ease-In-Out**: For elements changing state

### Durations
- **Fast**: 150ms - Micro-interactions
- **Medium**: 300ms - State changes
- **Slow**: 500ms - Page transitions

### Reduced Motion
- **Respect Preferences**: Honor `prefers-reduced-motion` setting
- **Fallbacks**: Provide instant transitions when motion is reduced

## Dark Mode

### Implementation
- **CSS Classes**: Uses class-based dark mode with 'dark' class on html element
- **Color Tokens**: Semantic color tokens that change based on theme
- **Consistent Contrast**: Maintains accessibility standards in both themes

### Toggle Behavior
- **Persistent**: Theme preference saved to localStorage
- **System Integration**: Respects system dark mode preference initially
- **Smooth Transitions**: Animated transitions between themes

## Performance

### Optimization Strategies
- **Code Splitting**: Components loaded on-demand
- **Tree Shaking**: Unused code eliminated
- **Image Optimization**: Lazy loading and responsive images
- **Virtual Scrolling**: Large lists use virtual scrolling

### Bundle Analysis
- **Main Bundle**: Core application code
- **Vendor Bundle**: Third-party libraries
- **Chunk Analysis**: Regular analysis of bundle sizes

## Testing

### Accessibility Testing
- **Automated**: ESLint accessibility rules
- **Manual**: Regular screen reader testing
- **Compliance**: WCAG 2.1 AA validation

### Performance Testing
- **Lighthouse**: Regular Lighthouse audits
- **Core Web Vitals**: Monitoring of key performance metrics
- **Load Testing**: Testing with large datasets

## Implementation Guidelines

### File Structure
```
src/
├── components/
│   ├── ui/           # Base UI components
│   ├── layout/       # Layout components
│   └── domain/       # Domain-specific components
├── contexts/         # React contexts
├── hooks/           # Custom hooks
├── utils/           # Utility functions
└── styles/          # Global styles
```

### Naming Conventions
- **Components**: PascalCase (e.g., `StatusBadge`)
- **Files**: PascalCase for components, camelCase for utilities
- **CSS Classes**: Tailwind utility classes
- **Props**: camelCase

### Code Organization
- **Single Responsibility**: Each component has one clear purpose
- **Composition**: Prefer composition over inheritance
- **Accessibility**: Built-in accessibility features
- **Performance**: Optimized for performance by default

## Usage Examples

### Theme Toggle
```tsx
import { useTheme } from '../contexts/ThemeContext';
import ThemeToggle from '../components/ThemeToggle';

const MyComponent = () => {
  const { theme } = useTheme();
  return <ThemeToggle />;
};
```

### Status Badge
```tsx
import StatusBadge from '../components/StatusBadge';

const MyComponent = () => (
  <StatusBadge 
    status="success" 
    label="Connected" 
    size="sm" 
    variant="soft" 
  />
);
```

### Virtual Scrolling
```tsx
import VirtualScroll from '../components/VirtualScroll';

const MyComponent = () => (
  <VirtualScroll
    items={largeDataset}
    itemHeight={60}
    containerHeight={400}
    renderItem={(item) => <div>{item.name}</div>}
  />
);
```

## Maintenance

### Regular Updates
- **Dependency Updates**: Keep dependencies current
- **Accessibility Audits**: Regular accessibility reviews
- **Performance Monitoring**: Continuous performance monitoring
- **Design System Updates**: Keep design system current

### Documentation
- **Component Documentation**: Document all components
- **Usage Examples**: Provide clear usage examples
- **Migration Guides**: Document breaking changes
- **Best Practices**: Share implementation best practices