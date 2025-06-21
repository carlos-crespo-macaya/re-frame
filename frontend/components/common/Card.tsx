import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  children: ReactNode;
  className?: string;
  as?: 'div' | 'section' | 'article';
  role?: string;
  'aria-label'?: string;
}

export function Card({
  children,
  className,
  as: Component = 'div',
  role,
  'aria-label': ariaLabel,
}: CardProps) {
  return (
    <Component
      className={cn(
        'bg-white dark:bg-neutral-900 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-800 p-6',
        className
      )}
      role={role}
      aria-label={ariaLabel}
    >
      {children}
    </Component>
  );
}