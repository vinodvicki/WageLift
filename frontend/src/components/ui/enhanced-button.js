/**
 * Enhanced Button Component - WageLift Design System
 * 
 * Professional button implementation following design system specifications.
 * Compatible with CDN-based React setup.
 */

// Button component with enhanced styling and functionality
const EnhancedButton = ({ 
  variant = 'primary', 
  size = 'lg', 
  loading = false, 
  leftIcon = null, 
  rightIcon = null, 
  fullWidth = false, 
  disabled = false, 
  className = '', 
  children,
  onClick,
  ...props 
}) => {
  // Base styles following design system
  const baseClasses = [
    'inline-flex', 'items-center', 'justify-center', 'font-semibold',
    'transition-all', 'duration-200', 'ease-out', 'cursor-pointer',
    'focus:outline-none', 'focus:ring-2', 'focus:ring-offset-2',
    'disabled:opacity-50', 'disabled:cursor-not-allowed',
    'disabled:transform-none', 'select-none'
  ];

  if (fullWidth) baseClasses.push('w-full');

  // Variant styles based on design system
  const variantClasses = {
    primary: [
      'bg-yellow-400', 'text-blue-900', 'font-semibold',
      'hover:bg-yellow-500', 'hover:scale-105', 'hover:shadow-lg',
      'focus:ring-yellow-400', 'active:scale-95',
      'border', 'border-yellow-400'
    ],
    secondary: [
      'bg-blue-600', 'text-white',
      'hover:bg-blue-700', 'hover:scale-105', 'hover:shadow-lg',
      'focus:ring-blue-500', 'active:scale-95',
      'border', 'border-blue-600'
    ],
    outline: [
      'border-2', 'border-yellow-400', 'text-yellow-600', 'bg-transparent',
      'hover:bg-yellow-400', 'hover:text-blue-900', 'hover:scale-105',
      'focus:ring-yellow-400', 'active:scale-95'
    ],
    ghost: [
      'text-blue-600', 'bg-transparent',
      'hover:bg-blue-50', 'hover:text-blue-700',
      'focus:ring-blue-500'
    ]
  };

  // Size styles based on design system (48px height for lg)
  const sizeClasses = {
    sm: ['h-8', 'px-3', 'text-sm', 'rounded-md', 'gap-1.5'],
    md: ['h-10', 'px-4', 'text-base', 'rounded-lg', 'gap-2'],
    lg: ['h-12', 'px-6', 'text-lg', 'rounded-xl', 'gap-2.5'], // 48px height
    xl: ['h-14', 'px-8', 'text-xl', 'rounded-2xl', 'gap-3']
  };

  // Loading spinner
  const LoadingSpinner = () => 
    React.createElement('svg', {
      className: 'animate-spin h-4 w-4',
      xmlns: 'http://www.w3.org/2000/svg',
      fill: 'none',
      viewBox: '0 0 24 24'
    }, [
      React.createElement('circle', {
        key: 'circle',
        className: 'opacity-25',
        cx: '12',
        cy: '12',
        r: '10',
        stroke: 'currentColor',
        strokeWidth: '4'
      }),
      React.createElement('path', {
        key: 'path',
        className: 'opacity-75',
        fill: 'currentColor',
        d: 'M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
      })
    ]);

  // Combine all classes
  const allClasses = [
    ...baseClasses,
    ...variantClasses[variant] || variantClasses.primary,
    ...sizeClasses[size] || sizeClasses.lg,
    className
  ].join(' ');

  // Button content
  const buttonContent = loading ? [
    React.createElement(LoadingSpinner, { key: 'spinner' }),
    children && React.createElement('span', { key: 'text', className: 'ml-2' }, children)
  ] : [
    leftIcon && React.createElement('span', { key: 'left-icon', className: 'flex-shrink-0' }, leftIcon),
    children && React.createElement('span', { key: 'children' }, children),
    rightIcon && React.createElement('span', { key: 'right-icon', className: 'flex-shrink-0' }, rightIcon)
  ].filter(Boolean);

  return React.createElement('button', {
    className: allClasses,
    disabled: disabled || loading,
    onClick: onClick,
    ...props
  }, ...buttonContent);
};

// Card component following design system
const EnhancedCard = ({ 
  children, 
  className = '', 
  padding = 'lg',
  shadow = 'md',
  ...props 
}) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6', 
    lg: 'p-8',  // 32px padding
    xl: 'p-10'
  };

  const shadowClasses = {
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl'
  };

  const cardClasses = [
    'bg-white', 'rounded-xl', 'border', 'border-gray-200',
    paddingClasses[padding] || paddingClasses.lg,
    shadowClasses[shadow] || shadowClasses.md,
    className
  ].join(' ');

  return React.createElement('div', {
    className: cardClasses,
    ...props
  }, children);
};

// Input component following design system
const EnhancedInput = ({ 
  label,
  error,
  className = '',
  ...props 
}) => {
  const inputClasses = [
    'w-full', 'h-12', 'px-4', 'py-3', 'rounded-lg', 'border',
    'border-gray-300', 'bg-white', 'text-gray-900',
    'placeholder-gray-500', 'transition-all', 'duration-200',
    'focus:outline-none', 'focus:ring-2', 'focus:ring-yellow-400',
    'focus:border-yellow-400', 'disabled:bg-gray-50',
    'disabled:text-gray-500', 'disabled:cursor-not-allowed',
    error ? 'border-red-500 focus:ring-red-400 focus:border-red-400' : '',
    className
  ].filter(Boolean).join(' ');

  return React.createElement('div', { className: 'space-y-2' }, [
    label && React.createElement('label', { 
      key: 'label',
      className: 'block text-sm font-medium text-gray-700' 
    }, label),
    React.createElement('input', {
      key: 'input',
      className: inputClasses,
      ...props
    }),
    error && React.createElement('p', {
      key: 'error',
      className: 'text-sm text-red-600'
    }, error)
  ].filter(Boolean));
};

// Navigation component following design system
const EnhancedNavigation = ({ children, className = '' }) => {
  const navClasses = [
    'sticky', 'top-0', 'z-50', 'h-20', 'bg-white', 'bg-opacity-96',
    'backdrop-blur-sm', 'border-b', 'border-gray-200',
    'transition-all', 'duration-200',
    className
  ].join(' ');

  return React.createElement('nav', { className: navClasses }, 
    React.createElement('div', { 
      className: 'container mx-auto px-4 h-full flex items-center justify-between' 
    }, children)
  );
};

// Hero section component
const EnhancedHero = ({ 
  title, 
  subtitle, 
  primaryAction, 
  secondaryAction,
  illustration,
  className = '' 
}) => {
  const heroClasses = [
    'relative', 'overflow-hidden', 'py-20', 'lg:py-32',
    'bg-gradient-to-br', 'from-blue-600', 'to-blue-800',
    className
  ].join(' ');

  return React.createElement('section', { className: heroClasses }, [
    // Background pattern
    React.createElement('div', {
      key: 'bg-pattern',
      className: 'absolute inset-0 bg-grid-white/[0.05] bg-[size:60px_60px]'
    }),
    
    // Content container
    React.createElement('div', {
      key: 'content',
      className: 'relative container mx-auto px-4'
    }, [
      React.createElement('div', {
        key: 'grid',
        className: 'grid lg:grid-cols-2 gap-12 items-center'
      }, [
        // Text content
        React.createElement('div', {
          key: 'text',
          className: 'text-white space-y-8'
        }, [
          React.createElement('h1', {
            key: 'title',
            className: 'text-4xl lg:text-6xl font-bold leading-tight'
          }, title),
          subtitle && React.createElement('p', {
            key: 'subtitle',
            className: 'text-xl lg:text-2xl text-blue-100 leading-relaxed'
          }, subtitle),
          React.createElement('div', {
            key: 'actions',
            className: 'flex flex-col sm:flex-row gap-4'
          }, [
            primaryAction,
            secondaryAction
          ].filter(Boolean))
        ]),
        
        // Illustration
        illustration && React.createElement('div', {
          key: 'illustration',
          className: 'relative'
        }, illustration)
      ])
    ])
  ]);
};

// Export components for global use
window.WageLiftUI = {
  EnhancedButton,
  EnhancedCard,
  EnhancedInput,
  EnhancedNavigation,
  EnhancedHero
}; 