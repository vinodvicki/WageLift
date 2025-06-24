/**
 * WageLift Design System - Design Tokens
 * Professional UI/UX Design System with enhanced scalability and maintainability
 * 
 * Based on client specifications with professional optimizations:
 * - Enhanced color palette with semantic tokens
 * - Scalable typography with fluid sizing
 * - Comprehensive spacing and layout tokens
 * - Animation and interaction tokens
 * - Accessibility-first approach
 */

// =============================================================================
// CORE DESIGN TOKENS
// =============================================================================

export const designTokens = {
  // ---------------------------------------------------------------------------
  // COLOR SYSTEM - Enhanced with semantic tokens
  // ---------------------------------------------------------------------------
  colors: {
    // Primary Brand Colors
    primary: {
      50: '#F0F4FF',   // Lightest blue tint
      100: '#E0EAFF',  // Light blue tint
      200: '#C7D8FF',  // Medium light blue
      300: '#A3C1FF',  // Medium blue
      400: '#7BA3FF',  // Medium dark blue
      500: '#4C5B9C',  // Brand secondary
      600: '#2B3A67',  // Deep Ocean Blue (primary)
      700: '#1E2B4F',  // Darker blue
      800: '#141D37',  // Very dark blue
      900: '#0A1020',  // Almost black blue
    },
    
    // Accent Colors
    accent: {
      50: '#FFFBF0',   // Lightest yellow tint
      100: '#FFF5E0',  // Light yellow tint
      200: '#FFEBCC',  // Medium light yellow
      300: '#FFD999',  // Medium yellow
      400: '#FFCC66',  // Medium bright yellow
      500: '#FFC857',  // Acid Yellow (primary accent)
      600: '#E6B34F',  // Darker yellow
      700: '#CC9E47',  // Dark yellow
      800: '#B3893F',  // Very dark yellow
      900: '#997437',  // Darkest yellow
    },
    
    // Neutral Colors - Enhanced with warm undertones
    neutral: {
      0: '#FFFFFF',     // Pure white
      50: '#FAFAFA',    // Off-white (enhanced)
      100: '#F5F5F5',   // Off-White (original)
      200: '#E8E8E8',   // Lighter gray
      300: '#E0E0E0',   // Warm Gray (original)
      400: '#C4C4C4',   // Medium light gray
      500: '#9CA3AF',   // Medium gray
      600: '#6B7280',   // Medium dark gray
      700: '#444444',   // Gunmetal (original)
      800: '#1F2937',   // Dark gray
      900: '#111827',   // Almost black
    },
    
    // Semantic Colors - Enhanced feedback system
    semantic: {
      success: {
        50: '#F0FDF4',
        100: '#DCFCE7',
        500: '#3CB043',  // Success Green (original)
        600: '#16A34A',
        700: '#15803D',
      },
      warning: {
        50: '#FFFBEB',
        100: '#FEF3C7',
        500: '#F5A623',  // Warning Amber (original)
        600: '#D97706',
        700: '#B45309',
      },
      error: {
        50: '#FEF2F2',
        100: '#FEE2E2',
        500: '#E02F2F',  // Error Red (original)
        600: '#DC2626',
        700: '#B91C1C',
      },
      info: {
        50: '#EFF6FF',
        100: '#DBEAFE',
        500: '#3B82F6',
        600: '#2563EB',
        700: '#1D4ED8',
      },
    },
    
    // Surface Colors - For layered UI
    surface: {
      background: '#FAFAFA',      // Main background
      card: '#FFFFFF',           // Card backgrounds
      elevated: '#FFFFFF',       // Elevated surfaces
      overlay: 'rgba(0,0,0,0.5)', // Modal overlays
      border: '#E0E0E0',         // Border color
      divider: '#F3F4F6',        // Subtle dividers
    },
  },

  // ---------------------------------------------------------------------------
  // TYPOGRAPHY SYSTEM - Enhanced with fluid scaling
  // ---------------------------------------------------------------------------
  typography: {
    // Font Families
    fontFamily: {
      headline: ['GT Sectra', 'Tiempos', 'Georgia', 'serif'],
      body: ['Inter', 'Graphik', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'SF Mono', 'Monaco', 'monospace'],
    },
    
    // Font Weights
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    
    // Font Sizes - Enhanced with responsive scaling
    fontSize: {
      // Display sizes for hero sections
      display: {
        sm: 'clamp(2.5rem, 4vw, 3rem)',      // 40-48px
        md: 'clamp(3rem, 5vw, 3.75rem)',     // 48-60px
        lg: 'clamp(3.75rem, 6vw, 4.5rem)',   // 60-72px
      },
      
      // Heading sizes
      heading: {
        h1: 'clamp(2rem, 3vw, 3rem)',        // 32-48px
        h2: 'clamp(1.75rem, 2.5vw, 2.25rem)', // 28-36px
        h3: 'clamp(1.5rem, 2vw, 1.75rem)',   // 24-28px
        h4: 'clamp(1.25rem, 1.5vw, 1.5rem)', // 20-24px
        h5: '1.125rem',                       // 18px
        h6: '1rem',                           // 16px
      },
      
      // Body text sizes
      body: {
        lg: '1.125rem',    // 18px (original body)
        md: '1rem',        // 16px (small text)
        sm: '0.875rem',    // 14px (caption)
        xs: '0.75rem',     // 12px (fine print)
      },
      
      // UI component sizes
      ui: {
        button: '1rem',      // 16px
        input: '1rem',       // 16px
        label: '0.875rem',   // 14px
        caption: '0.75rem',  // 12px
      },
    },
    
    // Line Heights
    lineHeight: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.6,   // Original specification
      loose: 1.8,
    },
    
    // Letter Spacing
    letterSpacing: {
      tight: '-0.025em',
      normal: '0',
      wide: '0.025em',
      wider: '0.05em',
    },
  },

  // ---------------------------------------------------------------------------
  // SPACING SYSTEM - Enhanced with semantic tokens
  // ---------------------------------------------------------------------------
  spacing: {
    // Base spacing scale (8px unit system)
    scale: {
      0: '0',
      1: '0.25rem',    // 4px
      2: '0.5rem',     // 8px (base unit)
      3: '0.75rem',    // 12px
      4: '1rem',       // 16px
      5: '1.25rem',    // 20px
      6: '1.5rem',     // 24px
      8: '2rem',       // 32px
      10: '2.5rem',    // 40px
      12: '3rem',      // 48px
      16: '4rem',      // 64px
      20: '5rem',      // 80px
      24: '6rem',      // 96px
      32: '8rem',      // 128px
    },
    
    // Semantic spacing tokens
    component: {
      button: {
        padding: '0.75rem 1.5rem',  // 12px 24px
        gap: '0.5rem',              // 8px
      },
      input: {
        padding: '0.75rem 1rem',    // 12px 16px (original)
        gap: '0.5rem',              // 8px
      },
      card: {
        padding: '1.5rem',          // 24px
        gap: '1rem',                // 16px
      },
      section: {
        padding: '3rem 0',          // 48px vertical
        gap: '1.5rem',              // 24px (original vertical rhythm)
      },
    },
    
    // Layout spacing
    layout: {
      container: {
        mobile: '1rem',     // 16px (original)
        tablet: '1.5rem',   // 24px (original)
        desktop: '2rem',    // 32px
      },
      grid: {
        gap: '1.5rem',      // 24px (original gutter)
        column: '1fr',      // 12-column grid
      },
    },
  },

  // ---------------------------------------------------------------------------
  // LAYOUT SYSTEM - Enhanced grid and breakpoints
  // ---------------------------------------------------------------------------
  layout: {
    // Breakpoints - Enhanced with more granular control
    breakpoints: {
      xs: '0px',
      sm: '640px',     // Mobile
      md: '768px',     // Tablet
      lg: '1024px',    // Desktop
      xl: '1280px',    // Large desktop
      '2xl': '1536px', // Extra large
    },
    
    // Container sizes
    container: {
      sm: '640px',
      md: '768px',     // Tablet max (original: 720px)
      lg: '1024px',
      xl: '1200px',    // Desktop max (original)
      '2xl': '1536px',
    },
    
    // Grid system
    grid: {
      columns: 12,     // Original specification
      gap: '1.5rem',   // 24px (original)
    },
    
    // Z-index scale
    zIndex: {
      hide: -1,
      auto: 'auto',
      base: 0,
      docked: 10,
      dropdown: 1000,
      sticky: 1100,
      banner: 1200,
      overlay: 1300,
      modal: 1400,
      popover: 1500,
      tooltip: 1600,
      toast: 1700,
    },
  },

  // ---------------------------------------------------------------------------
  // COMPONENT TOKENS - Enhanced with interaction states
  // ---------------------------------------------------------------------------
  components: {
    // Navigation
    navigation: {
      height: '5rem',        // 80px (original)
      backdrop: 'rgba(255, 255, 255, 0.96)', // Original backdrop-blur
      linkPadding: '1.5rem', // 24px horizontal (original)
      underlineHeight: '2px',
    },
    
    // Buttons - Enhanced with more variants
    button: {
      height: {
        sm: '2rem',          // 32px
        md: '2.5rem',        // 40px
        lg: '3rem',          // 48px (original primary)
        xl: '3.5rem',        // 56px
      },
      borderRadius: {
        sm: '0.375rem',      // 6px
        md: '0.5rem',        // 8px
        lg: '1.5rem',        // 24px (pill shape)
        full: '9999px',      // Full pill
      },
      padding: {
        sm: '0.5rem 0.75rem',
        md: '0.75rem 1rem',
        lg: '1rem 1.5rem',   // Original specification
        xl: '1.25rem 2rem',
      },
    },
    
    // Cards - Enhanced with elevation system
    card: {
      borderRadius: '0.75rem',  // 12px (original)
      shadow: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        md: '0 4px 12px rgba(0, 0, 0, 0.05)', // Original
        lg: '0 8px 24px rgba(0, 0, 0, 0.1)',  // Modal shadow
        xl: '0 20px 40px rgba(0, 0, 0, 0.1)',
      },
      border: '1px solid #E0E0E0', // Original
    },
    
    // Forms
    form: {
      input: {
        height: '3rem',        // 48px
        borderRadius: '0.5rem', // 8px (original)
        border: '1px solid #E0E0E0',
        shadow: 'inset 0 2px 4px rgba(0,0,0,0.06)', // Original
        focusRing: '0 0 0 2px #FFC857', // Acid yellow
      },
    },
  },

  // ---------------------------------------------------------------------------
  // ANIMATION SYSTEM - Enhanced with performance-first approach
  // ---------------------------------------------------------------------------
  animation: {
    // Timing functions
    easing: {
      linear: 'linear',
      ease: 'ease',
      easeIn: 'ease-in',
      easeOut: 'ease-out',
      easeInOut: 'ease-in-out',
      custom: 'cubic-bezier(0.22, 1, 0.36, 1)', // Original smooth easing
      spring: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    },
    
    // Duration scale
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '600ms',    // Original hero animation
      slower: '1000ms',
    },
    
    // Common animations
    keyframes: {
      fadeIn: {
        from: { opacity: 0 },
        to: { opacity: 1 },
      },
      slideUp: {
        from: { transform: 'translateY(20px)', opacity: 0 },
        to: { transform: 'translateY(0)', opacity: 1 },
      },
      scaleIn: {
        from: { transform: 'scale(0.95)', opacity: 0 },
        to: { transform: 'scale(1)', opacity: 1 },
      },
      shimmer: {
        '0%': { backgroundPosition: '-200px 0' },
        '100%': { backgroundPosition: 'calc(200px + 100%) 0' },
      },
    },
    
    // Interaction states
    hover: {
      scale: 1.03,      // Original button hover
      duration: '200ms',
    },
    
    // Loading states
    loading: {
      shimmer: {
        background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
        animation: 'shimmer 1.5s infinite',
      },
      spinner: {
        size: '1.5rem',
        thickness: '2px',
        color: '#FFC857', // Acid yellow
      },
    },
  },

  // ---------------------------------------------------------------------------
  // ACCESSIBILITY TOKENS
  // ---------------------------------------------------------------------------
  accessibility: {
    // Focus management
    focus: {
      ring: {
        width: '2px',
        color: '#FFC857',    // Acid yellow
        offset: '2px',
      },
    },
    
    // Touch targets
    touch: {
      minSize: '44px',       // Original mobile specification
      comfortable: '48px',
    },
    
    // Contrast ratios (WCAG AA compliant)
    contrast: {
      minimum: 4.5,          // Original specification
      enhanced: 7,           // AAA level
    },
  },

  // ---------------------------------------------------------------------------
  // PERFORMANCE TOKENS
  // ---------------------------------------------------------------------------
  performance: {
    // Critical metrics
    metrics: {
      lcp: 1500,             // 1.5s (original)
      tti: 3000,             // 3s (original)
      bundleSize: 204800,    // 200KB gzipped (original)
    },
    
    // Optimization thresholds
    optimization: {
      imageMaxSize: 1024,    // 1MB
      fontPreload: ['Inter', 'GT Sectra'],
      criticalCss: true,     // Original specification
    },
  },
} as const;

// =============================================================================
// TYPE DEFINITIONS
// =============================================================================

export type ColorToken = keyof typeof designTokens.colors;
export type SpacingToken = keyof typeof designTokens.spacing.scale;
export type TypographyToken = keyof typeof designTokens.typography.fontSize;
export type AnimationToken = keyof typeof designTokens.animation.duration;

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Get design token value with fallback
 */
export function getToken<T>(path: string, fallback?: T): T | string {
  const keys = path.split('.');
  let current: any = designTokens;
  
  for (const key of keys) {
    if (current?.[key] === undefined) {
      return fallback as T;
    }
    current = current[key];
  }
  
  return current;
}

/**
 * Generate CSS custom properties from design tokens
 */
export function generateCSSVariables(): Record<string, string> {
  const variables: Record<string, string> = {};
  
  function traverse(obj: any, prefix = '--wagelift'): void {
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const value = obj[key];
        const cssVar = `${prefix}-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
        
        if (typeof value === 'object' && value !== null) {
          traverse(value, cssVar);
        } else {
          variables[cssVar] = String(value);
        }
      }
    }
  }
  
  traverse(designTokens);
  return variables;
}

/**
 * Responsive breakpoint helper
 */
export function breakpoint(size: keyof typeof designTokens.layout.breakpoints): string {
  return `@media (min-width: ${designTokens.layout.breakpoints[size]})`;
}

export default designTokens; 