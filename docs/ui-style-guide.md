# BigShot UI Style Guide

## Overview

The BigShot UI design system follows modern FANG-style aesthetics with clean, neutral colors, excellent typography, and consistent spacing. This guide documents the design principles and components used throughout the application.

## Design Principles

### 1. Clarity & Readability
- High contrast for accessibility (WCAG 2.1 AA compliant)
- Clear visual hierarchy with proper spacing
- Consistent typography with excellent readability

### 2. Modern Minimalism
- Clean, uncluttered interfaces
- Subtle shadows and borders
- Generous white space
- Reduced visual noise

### 3. User-Centric Design
- Touch-friendly interactive elements (minimum 44px targets)
- Predictable interactions and feedback
- Responsive design for all screen sizes
- Keyboard navigation support

## Color Palette

### Primary Colors (Neutral)
```css
/* Light to Dark Grays */
neutral-50:  #fafafa
neutral-100: #f5f5f5
neutral-200: #e5e5e5
neutral-300: #d4d4d4
neutral-400: #a3a3a3
neutral-500: #737373
neutral-600: #525252
neutral-700: #404040
neutral-800: #262626
neutral-900: #171717
neutral-950: #0a0a0a
```

### Accent Colors (Blue)
```css
/* Interactive Elements */
accent-50:  #eff6ff
accent-100: #dbeafe
accent-200: #bfdbfe
accent-300: #93c5fd
accent-400: #60a5fa
accent-500: #3b82f6  /* Primary */
accent-600: #2563eb  /* Primary Hover */
accent-700: #1d4ed8
accent-800: #1e40af
accent-900: #1e3a8a
accent-950: #172554
```

### Status Colors
```css
/* Success */
success-500: #22c55e
success-600: #16a34a

/* Warning */
warning-500: #eab308
warning-600: #ca8a04

/* Error */
error-500: #ef4444
error-600: #dc2626
```

### Dark Mode Colors
```css
/* Dark Theme Backgrounds */
dark-800: #262626  /* Component backgrounds */
dark-900: #171717  /* Section backgrounds */
dark-950: #0a0a0a  /* Page backgrounds */
```

## Typography

### Font Stack
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

### Font Weights
- **Light (300)**: Used sparingly for large display text
- **Regular (400)**: Body text, descriptions
- **Medium (500)**: Labels, captions
- **Semibold (600)**: Headings, buttons, emphasis
- **Bold (700)**: Major headings, strong emphasis

### Font Sizes & Line Heights
```css
/* Headings */
h1: 1.875rem (30px) / line-height: 1.25
h2: 1.5rem (24px) / line-height: 1.25
h3: 1.25rem (20px) / line-height: 1.25
h4: 1.125rem (18px) / line-height: 1.25

/* Body Text */
base: 1rem (16px) / line-height: 1.6
small: 0.875rem (14px) / line-height: 1.5
xs: 0.75rem (12px) / line-height: 1.4
```

### Typography Features
- Letter spacing: -0.025em for headings (improved readability)
- OpenType features enabled: cv02, cv03, cv04, cv11
- Anti-aliasing: optimized for screens

## Spacing System

### Scale (based on 4px grid)
```css
xs:  4px
sm:  8px
md:  12px
lg:  16px
xl:  20px
2xl: 24px
3xl: 32px
4xl: 40px
5xl: 48px
6xl: 64px
```

### Component Spacing
- **Form inputs**: 12px padding (vertical), 16px padding (horizontal)
- **Buttons**: 12px padding (vertical), 16px padding (horizontal)
- **Cards**: 24px padding
- **Sections**: 32px margin between major sections

## Shadows & Elevation

### Shadow Levels
```css
/* Subtle elevation */
soft: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)

/* Medium elevation */
medium: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)

/* Strong elevation */
strong: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)

/* Focus ring */
focus: 0 0 0 3px rgba(59, 130, 246, 0.1)
```

## Border Radius

### Scale
```css
sm:  6px   /* Small elements, inputs */
md:  8px   /* Buttons, small cards */
lg:  12px  /* Cards, panels */
xl:  16px  /* Large cards */
2xl: 20px  /* Modals, major containers */
```

## Interactive Elements

### Buttons

#### Primary Button
```css
/* Light Mode */
background: accent-600 (#2563eb)
color: white
hover: accent-700 (#1d4ed8)
focus: ring-2 ring-accent-500

/* Dark Mode */
Same as light mode (sufficient contrast)
```

#### Secondary Button
```css
/* Light Mode */
background: neutral-100 (#f5f5f5)
color: neutral-900 (#171717)
border: 1px solid neutral-300 (#d4d4d4)
hover: neutral-200 (#e5e5e5)

/* Dark Mode */
background: dark-700 (#404040)
color: white
border: 1px solid dark-600 (#525252)
hover: dark-600 (#525252)
```

### Form Inputs
```css
/* Base Styles */
padding: 12px 16px
border-radius: 12px
border: 1px solid neutral-300
focus: ring-2 ring-accent-500, border-accent-500

/* Light Mode */
background: white
color: neutral-900
placeholder: neutral-500

/* Dark Mode */
background: dark-700 (#404040)
color: white
border: dark-600 (#525252)
placeholder: neutral-400
```

### Navigation
```css
/* Active State */
background: accent-100 (light) / accent-900/20 (dark)
color: accent-900 (light) / accent-100 (dark)

/* Hover State */
background: neutral-100 (light) / dark-700 (dark)
color: neutral-900 (light) / white (dark)
```

## Component Guidelines

### Cards
- Use `shadow-medium` for elevation
- `border-radius: 16px` for modern appearance
- `border: 1px solid neutral-200` (light) / `dark-700` (dark)
- Consistent 24px padding

### Modals & Overlays
- Backdrop: `bg-black bg-opacity-50`
- Container: `shadow-strong` with `border-radius: 20px`
- Maximum width constraints for readability

### Status Indicators
- Use semantic colors (success, warning, error)
- Include icons for better accessibility
- Consistent badge styling with proper padding

## Responsive Design

### Breakpoints
```css
sm:  640px   /* Small tablets */
md:  768px   /* Tablets */
lg:  1024px  /* Small desktops */
xl:  1280px  /* Desktops */
2xl: 1536px  /* Large desktops */
```

### Layout Principles
- Mobile-first approach
- Flexible grid systems
- Collapsible navigation on mobile
- Touch-friendly interactions (minimum 44px targets)

## Accessibility Features

### Focus Management
- Visible focus indicators on all interactive elements
- Logical tab order
- Skip links for keyboard navigation

### Color & Contrast
- WCAG 2.1 AA compliant contrast ratios
- No reliance on color alone for information
- High contrast mode support

### Typography
- Minimum 16px font size for body text
- Relative units (rem/em) for scalability
- Proper heading hierarchy

## Animation & Transitions

### Timing
```css
/* Standard transitions */
duration: 200ms
easing: ease-in-out

/* Micro-interactions */
duration: 150ms
easing: ease-out

/* Page transitions */
duration: 300ms
easing: ease-in-out
```

### Reduced Motion
- Respect `prefers-reduced-motion` setting
- Minimal animation for users who prefer it
- Essential motion only (loading states, etc.)

## Implementation Notes

### CSS Framework
- Built with Tailwind CSS
- Custom design tokens defined in `tailwind.config.js`
- Utility-first approach with component abstractions

### Dark Mode
- System preference detection
- Manual toggle available
- Consistent color relationships across themes

### Browser Support
- Modern browsers (last 2 versions)
- Progressive enhancement for older browsers
- Graceful degradation of advanced features

## Usage Examples

### Button Implementation
```jsx
<button className="px-4 py-3 bg-accent-600 text-white rounded-xl hover:bg-accent-700 focus:outline-none focus:ring-2 focus:ring-accent-500 transition-colors duration-200">
  Primary Action
</button>
```

### Form Input Implementation
```jsx
<input className="w-full px-4 py-3 bg-white dark:bg-dark-700 border border-neutral-300 dark:border-dark-600 text-neutral-900 dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors" />
```

### Card Implementation
```jsx
<div className="bg-white dark:bg-dark-800 rounded-2xl p-6 shadow-medium border border-neutral-200 dark:border-dark-700">
  Card Content
</div>
```

## Future Considerations

### Planned Improvements
- Enhanced animation system
- Component library expansion
- Advanced theming capabilities
- Design token automation

### Performance
- CSS-in-JS migration potential
- Component lazy loading
- Critical CSS optimization
- Design system as npm package

---

This style guide should be updated as the design system evolves. For questions or contributions, please refer to the main project documentation.