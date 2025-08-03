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
    bg-[#9BF7EB] text-[#002e34] font-semibold
    hover:bg-[#7EEBD9] active:bg-[#65D9C6]
    focus-visible:ring-2 focus-visible:ring-[#9BF7EB]/35
  `,
  secondary: `
    bg-transparent text-[#9BF7EB] border border-[#9BF7EB]/30
    hover:bg-[#9BF7EB] hover:text-[#002e34] hover:border-[#9BF7EB]
    active:bg-[#7EEBD9] active:text-[#002e34]
    focus-visible:ring-2 focus-visible:ring-[#9BF7EB]/35
  `,
  outline: `
    bg-transparent text-[#9BF7EB] border border-[#9BF7EB]
    hover:bg-[#9BF7EB]/10 active:bg-[#9BF7EB]/20
    focus-visible:ring-2 focus-visible:ring-[#9BF7EB]/35
  `,
  ghost: `
    bg-transparent text-[#999999]
    hover:text-[#9BF7EB] hover:bg-[#9BF7EB]/10
    active:bg-[#9BF7EB]/20
    focus-visible:ring-2 focus-visible:ring-[#9BF7EB]/35
  `,
  danger: `
    bg-red-600 text-white
    hover:bg-red-700 active:bg-red-800
    focus-visible:ring-2 focus-visible:ring-red-500
  `,
};

const sizeClasses: Record<ButtonSize, string> = {
  small: 'px-3 py-1.5 text-sm min-h-[36px]',
  medium: 'px-4 py-2 text-sm md:px-6 md:py-3 md:text-base min-h-[44px]',
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
      font-medium rounded-2xl
      transition-colors duration-200 ease-smooth
      focus-visible:outline-none focus-visible:ring-offset-2
      focus-visible:ring-offset-[#08141c]
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
    // Note on ARIA:
    // - aria-busy expects a boolean token (true/false). Some linters/tools may misread expressions.
    // - To be maximally explicit and avoid false positives, we only include the attribute when true.
    return (
      <button
        ref={ref}
        type={type}
        className={baseClasses}
        disabled={disabled || loading}
        {...(loading ? { 'aria-busy': true } : {})}
        {...props}
      >
        {content}
      </button>
    );
  }
);

Button.displayName = 'Button';
