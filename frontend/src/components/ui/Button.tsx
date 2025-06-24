/**
 * Button Component - WageLift Design System
 * 
 * Professional button implementation with multiple variants, sizes, and states.
 * Follows the design system specifications with enhanced accessibility and performance.
 */

import React, { forwardRef, ButtonHTMLAttributes } from 'react';
import { designTokens } from '../../design-system/design-tokens';

// =============================================================================
// TYPES & INTERFACES
// =============================================================================

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button visual variant */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  /** Button size */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Loading state */
  loading?: boolean;
  /** Icon before text */
  leftIcon?: React.ReactNode;
  /** Icon after text */
  rightIcon?: React.ReactNode;
  /** Full width button */
  fullWidth?: boolean;
  /** Custom CSS classes */
  className?: string;
}

// =============================================================================
// COMPONENT IMPLEMENTATION
// =============================================================================

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled = false,
      className = '',
      children,
      ...props
    },
    ref
  ) => {
    // Base styles following design system
    const baseStyles = `
      inline-flex items-center justify-center font-medium
      transition-all duration-200 ease-out
      focus:outline-none focus:ring-2 focus:ring-offset-2
      disabled:opacity-50 disabled:cursor-not-allowed
      disabled:transform-none
      ${fullWidth ? 'w-full' : ''}
    `;

    // Variant styles
    const variantStyles = {
      primary: `
        bg-accent-500 text-primary-700 
        hover:bg-accent-600 hover:scale-[1.03] hover:shadow-lg
        focus:ring-accent-500
        active:scale-[0.98]
      `,
      secondary: `
        bg-primary-600 text-white
        hover:bg-primary-700 hover:scale-[1.03] hover:shadow-lg
        focus:ring-primary-500
        active:scale-[0.98]
      `,
      outline: `
        border-2 border-accent-500 text-accent-600 bg-transparent
        hover:bg-accent-500 hover:text-primary-700 hover:scale-[1.03]
        focus:ring-accent-500
        active:scale-[0.98]
      `,
      ghost: `
        text-primary-600 bg-transparent
        hover:bg-primary-50 hover:text-primary-700
        focus:ring-primary-500
      `,
      danger: `
        bg-semantic-error-500 text-white
        hover:bg-semantic-error-600 hover:scale-[1.03] hover:shadow-lg
        focus:ring-semantic-error-500
        active:scale-[0.98]
      `,
    };

    // Size styles
    const sizeStyles = {
      sm: `h-8 px-3 text-sm rounded-md gap-1.5`,
      md: `h-10 px-4 text-base rounded-lg gap-2`,
      lg: `h-12 px-6 text-lg rounded-xl gap-2.5`, // Original 48px height
      xl: `h-14 px-8 text-xl rounded-2xl gap-3`,
    };

    // Loading spinner component
    const LoadingSpinner = () => (
      <svg
        className="animate-spin h-4 w-4"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    );

    // Combine all styles
    const combinedClassName = `
      ${baseStyles}
      ${variantStyles[variant]}
      ${sizeStyles[size]}
      ${className}
    `.replace(/\s+/g, ' ').trim();

    return (
      <button
        ref={ref}
        className={combinedClassName}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <>
            <LoadingSpinner />
            {children && <span className="ml-2">{children}</span>}
          </>
        ) : (
          <>
            {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
            {children}
            {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

// =============================================================================
// BUTTON GROUP COMPONENT
// =============================================================================

export interface ButtonGroupProps {
  children: React.ReactNode;
  className?: string;
  orientation?: 'horizontal' | 'vertical';
  spacing?: 'none' | 'sm' | 'md' | 'lg';
}

export const ButtonGroup: React.FC<ButtonGroupProps> = ({
  children,
  className = '',
  orientation = 'horizontal',
  spacing = 'md',
}) => {
  const orientationStyles = {
    horizontal: 'flex-row',
    vertical: 'flex-col',
  };

  const spacingStyles = {
    none: 'gap-0',
    sm: 'gap-2',
    md: 'gap-3',
    lg: 'gap-4',
  };

  return (
    <div
      className={`
        flex ${orientationStyles[orientation]} ${spacingStyles[spacing]}
        ${className}
      `.replace(/\s+/g, ' ').trim()}
    >
      {children}
    </div>
  );
};

// =============================================================================
// ICON BUTTON COMPONENT
// =============================================================================

export interface IconButtonProps extends Omit<ButtonProps, 'leftIcon' | 'rightIcon' | 'children'> {
  icon: React.ReactNode;
  'aria-label': string;
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ icon, size = 'md', className = '', ...props }, ref) => {
    const sizeStyles = {
      sm: 'w-8 h-8 p-1',
      md: 'w-10 h-10 p-2',
      lg: 'w-12 h-12 p-2.5',
      xl: 'w-14 h-14 p-3',
    };

    return (
      <Button
        ref={ref}
        size={size}
        className={`${sizeStyles[size]} ${className}`.trim()}
        {...props}
      >
        {icon}
      </Button>
    );
  }
);

IconButton.displayName = 'IconButton';

export default Button; 