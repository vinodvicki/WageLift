/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,html}",
    "./index.html",
    "./public/**/*.html"
  ],
  theme: {
    extend: {
      // =======================================================================
      // COLOR SYSTEM - Enhanced with design system specifications
      // =======================================================================
      colors: {
        // Primary Brand Colors (Deep Ocean Blue)
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
        
        // Accent Colors (Acid Yellow)
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
        
        // Enhanced Neutral Colors with warm undertones
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
      },
      
      // =======================================================================
      // TYPOGRAPHY SYSTEM - Enhanced with fluid scaling
      // =======================================================================
      fontFamily: {
        // Headline fonts (GT Sectra / Tiempos)
        headline: ['GT Sectra', 'Tiempos', 'Georgia', 'serif'],
        // Body fonts (Inter / Graphik)
        body: ['Inter', 'Graphik', 'system-ui', 'sans-serif'],
        // Monospace fonts (JetBrains Mono)
        mono: ['JetBrains Mono', 'SF Mono', 'Monaco', 'monospace'],
      },
      
      fontSize: {
        // Display sizes for hero sections (fluid scaling)
        'display-sm': 'clamp(2.5rem, 4vw, 3rem)',      // 40-48px
        'display-md': 'clamp(3rem, 5vw, 3.75rem)',     // 48-60px
        'display-lg': 'clamp(3.75rem, 6vw, 4.5rem)',   // 60-72px
        
        // Enhanced heading sizes (fluid scaling)
        'heading-h1': 'clamp(2rem, 3vw, 3rem)',        // 32-48px
        'heading-h2': 'clamp(1.75rem, 2.5vw, 2.25rem)', // 28-36px
        'heading-h3': 'clamp(1.5rem, 2vw, 1.75rem)',   // 24-28px
        'heading-h4': 'clamp(1.25rem, 1.5vw, 1.5rem)', // 20-24px
        
        // Body text sizes
        'body-lg': '1.125rem',    // 18px (original body)
        'body-md': '1rem',        // 16px (small text)
        'body-sm': '0.875rem',    // 14px (caption)
        'body-xs': '0.75rem',     // 12px (fine print)
      },
      
      lineHeight: {
        'tight': 1.2,
        'normal': 1.5,
        'relaxed': 1.6,   // Original specification
        'loose': 1.8,
      },
      
      letterSpacing: {
        'tight': '-0.025em',
        'normal': '0',
        'wide': '0.025em',
        'wider': '0.05em',
      },
      
      // =======================================================================
      // SPACING SYSTEM - Enhanced 8px base unit system
      // =======================================================================
      spacing: {
        // Enhanced spacing scale
        '0.5': '0.125rem',    // 2px
        '1.5': '0.375rem',    // 6px
        '2.5': '0.625rem',    // 10px
        '3.5': '0.875rem',    // 14px
        '4.5': '1.125rem',    // 18px
        '5.5': '1.375rem',    // 22px
        '6.5': '1.625rem',    // 26px
        '7.5': '1.875rem',    // 30px
        '8.5': '2.125rem',    // 34px
        '9.5': '2.375rem',    // 38px
        '11': '2.75rem',      // 44px (touch target)
        '13': '3.25rem',      // 52px
        '15': '3.75rem',      // 60px
        '17': '4.25rem',      // 68px
        '18': '4.5rem',       // 72px
        '19': '4.75rem',      // 76px
        '21': '5.25rem',      // 84px
        '22': '5.5rem',       // 88px
        '80': '20rem',        // 320px (original nav height reference)
      },
      
      // =======================================================================
      // LAYOUT SYSTEM - Enhanced grid and container
      // =======================================================================
      container: {
        center: true,
        padding: {
          DEFAULT: '1rem',     // 16px (original mobile)
          sm: '1rem',          // 16px
          md: '1.5rem',        // 24px (original tablet)
          lg: '2rem',          // 32px
          xl: '2rem',          // 32px
          '2xl': '2rem',       // 32px
        },
        screens: {
          sm: '640px',
          md: '768px',         // Tablet max (close to original 720px)
          lg: '1024px',
          xl: '1200px',        // Desktop max (original)
          '2xl': '1536px',
        },
      },
      
      // =======================================================================
      // COMPONENT ENHANCEMENTS
      // =======================================================================
      borderRadius: {
        'xl': '0.75rem',     // 12px (original card radius)
        '2xl': '1rem',       // 16px
        '3xl': '1.5rem',     // 24px (pill shape)
      },
      
      boxShadow: {
        // Enhanced shadow system matching design specs
        'card': '0 4px 12px rgba(0, 0, 0, 0.05)',      // Original card shadow
        'card-hover': '0 8px 24px rgba(0, 0, 0, 0.1)', // Modal shadow
        'button': '0 2px 8px rgba(0, 0, 0, 0.1)',
        'button-hover': '0 4px 16px rgba(0, 0, 0, 0.15)',
        'input': 'inset 0 2px 4px rgba(0,0,0,0.06)',   // Original input shadow
      },
      
      // =======================================================================
      // ANIMATION SYSTEM - Performance-first approach
      // =======================================================================
      transitionDuration: {
        '200': '200ms',      // Button hover (original)
        '600': '600ms',      // Hero animation (original)
      },
      
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.22, 1, 0.36, 1)', // Original smooth easing
        'spring': 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      },
      
      scale: {
        '103': '1.03',       // Original button hover scale
        '98': '0.98',        // Active button scale
      },
      
      // =======================================================================
      // ANIMATION KEYFRAMES
      // =======================================================================
      keyframes: {
        'fade-in': {
          'from': { opacity: '0' },
          'to': { opacity: '1' },
        },
        'slide-up': {
          'from': { transform: 'translateY(20px)', opacity: '0' },
          'to': { transform: 'translateY(0)', opacity: '1' },
        },
        'scale-in': {
          'from': { transform: 'scale(0.95)', opacity: '0' },
          'to': { transform: 'scale(1)', opacity: '1' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200px 0' },
          '100%': { backgroundPosition: 'calc(200px + 100%) 0' },
        },
        'bounce-subtle': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-2px)' },
        },
      },
      
      animation: {
        'fade-in': 'fade-in 600ms ease-out',          // Hero copy animation
        'slide-up': 'slide-up 600ms ease-out',        // Hero slide animation
        'scale-in': 'scale-in 300ms ease-out',        // Modal entrance
        'shimmer': 'shimmer 1.5s infinite',           // Loading shimmer
        'bounce-subtle': 'bounce-subtle 2s infinite', // Icon hover effect
      },
      
      // =======================================================================
      // BACKDROP BLUR - For navigation
      // =======================================================================
      backdropBlur: {
        'nav': '24px',       // Navigation backdrop blur
      },
      
      // =======================================================================
      // Z-INDEX SCALE
      // =======================================================================
      zIndex: {
        'hide': '-1',
        'auto': 'auto',
        'base': '0',
        'docked': '10',
        'dropdown': '1000',
        'sticky': '1100',     // Navigation
        'banner': '1200',
        'overlay': '1300',
        'modal': '1400',
        'popover': '1500',
        'tooltip': '1600',
        'toast': '1700',
      },
      
      // =======================================================================
      // GRID ENHANCEMENTS
      // =======================================================================
      gridTemplateColumns: {
        // 12-column grid system (original specification)
        '12': 'repeat(12, minmax(0, 1fr))',
        // Feature grids
        'feature': 'repeat(auto-fit, minmax(300px, 1fr))',
        'auto-fill-300': 'repeat(auto-fill, minmax(300px, 1fr))',
      },
      
      gap: {
        // Grid gaps matching 24px specification
        'grid': '1.5rem',    // 24px (original gutter)
      },
    },
  },
  plugins: [
    // Add custom utilities
    function({ addUtilities, theme }) {
      const newUtilities = {
        // Touch-friendly button sizes
        '.btn-touch': {
          minHeight: '44px',   // Original mobile touch target
          minWidth: '44px',
        },
        
        // Navigation height utility
        '.nav-height': {
          height: '80px',      // Original specification
        },
        
        // Vertical rhythm utilities
        '.vertical-rhythm': {
          marginTop: '24px',   // Original vertical rhythm
          marginBottom: '24px',
        },
        
        // Focus ring utility matching design system
        '.focus-ring': {
          '&:focus': {
            outline: 'none',
            boxShadow: `0 0 0 2px ${theme('colors.accent.500')}`, // Acid yellow
          },
        },
        
        // Backdrop blur navigation
        '.nav-backdrop': {
          backgroundColor: 'rgba(255, 255, 255, 0.96)', // Original specification
          backdropFilter: 'blur(24px)',
        },
        
        // Card elevation system
        '.card-elevated': {
          boxShadow: theme('boxShadow.card'),
          '&:hover': {
            boxShadow: theme('boxShadow.card-hover'),
            transform: 'translateY(-2px)',
          },
        },
        
        // Button hover effects
        '.btn-hover-scale': {
          transition: 'all 200ms cubic-bezier(0.22, 1, 0.36, 1)',
          '&:hover:not(:disabled)': {
            transform: 'scale(1.03)',
          },
          '&:active:not(:disabled)': {
            transform: 'scale(0.98)',
          },
        },
        
        // Loading shimmer effect
        '.loading-shimmer': {
          background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
          backgroundSize: '200px 100%',
          animation: 'shimmer 1.5s infinite',
        },
      };
      
      addUtilities(newUtilities);
    },
    
    // Add component variants
    function({ addComponents, theme }) {
      const components = {
        // Primary button component
        '.btn-primary': {
          backgroundColor: theme('colors.accent.500'),
          color: theme('colors.primary.700'),
          fontWeight: theme('fontWeight.semibold'),
          height: '48px',                    // Original lg button height
          paddingLeft: theme('spacing.6'),   // 24px
          paddingRight: theme('spacing.6'),  // 24px
          borderRadius: theme('borderRadius.xl'),
          border: `1px solid ${theme('colors.accent.500')}`,
          transition: 'all 200ms cubic-bezier(0.22, 1, 0.36, 1)',
          '&:hover:not(:disabled)': {
            backgroundColor: theme('colors.accent.600'),
            transform: 'scale(1.03)',
            boxShadow: theme('boxShadow.button-hover'),
          },
          '&:focus': {
            outline: 'none',
            boxShadow: `0 0 0 2px ${theme('colors.accent.500')}`,
          },
          '&:active:not(:disabled)': {
            transform: 'scale(0.98)',
          },
          '&:disabled': {
            opacity: '0.5',
            cursor: 'not-allowed',
            transform: 'none',
          },
        },
        
        // Enhanced card component
        '.card': {
          backgroundColor: theme('colors.white'),
          borderRadius: theme('borderRadius.xl'),  // 12px (original)
          border: `1px solid ${theme('colors.neutral.300')}`, // Original border
          padding: theme('spacing.8'),             // 32px
          boxShadow: theme('boxShadow.card'),      // Original shadow
          transition: 'all 200ms ease-out',
        },
        
        // Enhanced input component
        '.input': {
          width: '100%',
          height: '48px',                          // Original specification
          paddingLeft: theme('spacing.4'),         // 16px (original)
          paddingRight: theme('spacing.4'),        // 16px (original)
          paddingTop: theme('spacing.3'),          // 12px (original)
          paddingBottom: theme('spacing.3'),       // 12px (original)
          borderRadius: theme('borderRadius.lg'),  // 8px (original)
          border: `1px solid ${theme('colors.neutral.300')}`,
          backgroundColor: theme('colors.white'),
          color: theme('colors.neutral.900'),
          boxShadow: theme('boxShadow.input'),     // Original inset shadow
          transition: 'all 200ms ease-out',
          '&:focus': {
            outline: 'none',
            borderColor: theme('colors.accent.500'),
            boxShadow: `0 0 0 2px ${theme('colors.accent.500')}`, // Original focus ring
          },
          '&::placeholder': {
            color: theme('colors.neutral.500'),
          },
          '&:disabled': {
            backgroundColor: theme('colors.neutral.50'),
            color: theme('colors.neutral.500'),
            cursor: 'not-allowed',
          },
        },
      };
      
      addComponents(components);
    },
  ],
} 