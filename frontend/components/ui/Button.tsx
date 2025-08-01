'use client';

import React, { forwardRef } from 'react';
import Link from 'next/link';
import LoadingSpinner from './LoadingSpinner';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
type ButtonSize = 'small' | 'medium' | 'large';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant | { base?: ButtonVariant; md?: ButtonVariant; lg?: ButtonVariant };
  size?: ButtonSize | { base?: ButtonSize; md?: ButtonSize; lg?: ButtonSize };
  fullWidth?: boolean;
  loading?: boolean;
  iconOnly?: boolean;
  href?: string;
  external?: boolean;
  children: React.ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: `
    bg-brand-green-600 text-white 
    hover:bg-brand-green-700 active:bg-brand-green-800
    focus-visible:ring-brand-green-500
  `,
  secondary: `
    bg-[#3a3a3a] text-[#EDEDED] border border-[#4a4a4a]
    hover:bg-[#4a4a4a] active:bg-[#5a5a5a]
    focus-visible:ring-brand-green-500
  `,
  outline: `
    bg-transparent text-brand-green-400 border border-brand-green-400
    hover:bg-brand-green-400/10 active:bg-brand-green-400/20
    focus-visible:ring-brand-green-500
  `,
  ghost: `
    bg-transparent text-[#999999]
    hover:bg-[#3a3a3a] active:bg-[#4a4a4a]
    focus-visible:ring-brand-green-500
  `,
  danger: `
    bg-red-600 text-white
    hover:bg-red-700 active:bg-red-800
    focus-visible:ring-red-500
  `,
};

const sizeClasses: Record<ButtonSize, string> = {
  small: 'px-3 py-1.5 text-sm min-h-[36px]',
  medium: 'px-4 py-2 text-base min-h-[44px]',
  large: 'px-6 py-3 text-lg min-h-[52px]',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'medium',
      fullWidth = false,
      loading = false,
      iconOnly = false,
      href,
      external = false,
      className = '',
      disabled = false,
      children,
      type = 'button',
      ...props
    },
    ref
  ) => {
    // Handle responsive variants and sizes
    const getVariantClasses = () => {
      if (typeof variant === 'object') {
        return variantClasses[variant.base || 'primary'];
      }
      return variantClasses[variant];
    };

    const getSizeClasses = () => {
      if (typeof size === 'object') {
        let classes = sizeClasses[size.base || 'medium'];
        if (size.md) classes += ` md:${sizeClasses[size.md]}`;
        if (size.lg) classes += ` lg:${sizeClasses[size.lg]}`;
        return classes;
      }
      return sizeClasses[size];
    };

    const baseClasses = `
      relative inline-flex items-center justify-center
      font-medium rounded-lg
      transition-all duration-200 ease-smooth
      focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2
      focus-visible:ring-offset-background
      disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none
      motion-safe:transform motion-safe:active:scale-[0.98]
      ${iconOnly ? 'p-2 aspect-square' : ''}
      ${fullWidth ? 'w-full' : ''}
      ${getVariantClasses()}
      ${getSizeClasses()}
      ${className}
    `.trim().replace(/\s+/g, ' ');

    const content = (
      <>
        {loading && (
          <span className="absolute inset-0 flex items-center justify-center" data-testid="button-spinner">
            <LoadingSpinner 
              size="sm" 
              showLabel={false}
              className="text-current"
            />
          </span>
        )}
        <span className={`flex items-center gap-2 ${loading ? 'invisible' : ''}`}>
          {children}
        </span>
      </>
    );

    // Render as link if href is provided
    if (href) {
      const linkProps = external
        ? { target: '_blank', rel: 'noopener noreferrer' }
        : {};

      return (
        <Link
          href={href}
          className={baseClasses}
          {...linkProps}
          aria-disabled={disabled || loading}
        >
          {content}
        </Link>
      );
    }

    // Render as button
    return (
      <button
        ref={ref}
        type={type}
        className={baseClasses}
        disabled={disabled || loading}
        aria-busy={loading ? "true" : "false"}
        {...props}
      >
        {content}
      </button>
    );
  }
);

Button.displayName = 'Button';