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
    bg-primary-500 text-white 
    hover:bg-primary-600 active:bg-primary-700
    focus-visible:ring-primary-500
    dark:bg-primary-600 dark:hover:bg-primary-700 dark:active:bg-primary-800
  `,
  secondary: `
    bg-neutral-100 text-neutral-900 border border-neutral-300
    hover:bg-neutral-200 active:bg-neutral-300
    focus-visible:ring-neutral-500
    dark:bg-neutral-800 dark:text-neutral-100 dark:border-neutral-700
    dark:hover:bg-neutral-700 dark:active:bg-neutral-600
  `,
  outline: `
    bg-transparent text-primary-600 border-2 border-primary-500
    hover:bg-primary-50 active:bg-primary-100
    focus-visible:ring-primary-500
    dark:text-primary-400 dark:border-primary-400
    dark:hover:bg-primary-950/20 dark:active:bg-primary-950/30
  `,
  ghost: `
    bg-transparent text-neutral-700
    hover:bg-neutral-100 active:bg-neutral-200
    focus-visible:ring-neutral-500
    dark:text-neutral-300 dark:hover:bg-neutral-800 dark:active:bg-neutral-700
  `,
  danger: `
    bg-error-500 text-white
    hover:bg-error-600 active:bg-error-700
    focus-visible:ring-error-500
    dark:bg-error-600 dark:hover:bg-error-700 dark:active:bg-error-800
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
        aria-busy={loading}
        {...props}
      >
        {content}
      </button>
    );
  }
);

Button.displayName = 'Button';