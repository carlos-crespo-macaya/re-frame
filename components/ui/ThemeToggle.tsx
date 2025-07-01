'use client';

import React from 'react';
import { useTheme } from '@/lib/theme/ThemeContext';

interface ThemeToggleProps {
  className?: string;
}

export function ThemeToggle({ className = '' }: ThemeToggleProps) {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  // Prevent hydration mismatch
  if (!mounted) {
    return (
      <div className={`h-10 w-10 rounded-lg bg-neutral-200 dark:bg-neutral-800 animate-pulse ${className}`} />
    );
  }

  const themes = [
    { value: 'light' as const, icon: '☀️', label: 'Light mode' },
    { value: 'dark' as const, icon: '🌙', label: 'Dark mode' },
    { value: 'system' as const, icon: '💻', label: 'System preference' },
  ];

  return (
    <div className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => {
          const currentIndex = themes.findIndex(t => t.value === theme);
          const nextIndex = (currentIndex + 1) % themes.length;
          setTheme(themes[nextIndex].value);
        }}
        className="group relative inline-flex h-10 w-10 items-center justify-center rounded-lg
                   bg-neutral-100 hover:bg-neutral-200 
                   dark:bg-neutral-800 dark:hover:bg-neutral-700
                   transition-all duration-200 ease-smooth
                   focus-visible:outline-none focus-visible:ring-2 
                   focus-visible:ring-primary-500 focus-visible:ring-offset-2
                   focus-visible:ring-offset-background"
        aria-label={`Current theme: ${themes.find(t => t.value === theme)?.label}. Click to change theme.`}
      >
        <span className="sr-only">Toggle theme</span>
        
        {/* Icons with smooth transitions */}
        <div className="relative h-5 w-5">
          {themes.map((t) => (
            <span
              key={t.value}
              className={`absolute inset-0 flex items-center justify-center
                         transition-all duration-300 ease-smooth
                         ${theme === t.value 
                           ? 'opacity-100 scale-100 rotate-0' 
                           : 'opacity-0 scale-75 rotate-180'}`}
              aria-hidden="true"
            >
              {t.icon}
            </span>
          ))}
        </div>
        
        {/* Tooltip */}
        <span className="absolute -bottom-12 left-1/2 -translate-x-1/2 
                         px-2 py-1 text-xs rounded-md
                         bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900
                         opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100
                         transition-opacity duration-200 pointer-events-none
                         whitespace-nowrap">
          {themes.find(t => t.value === theme)?.label}
        </span>
      </button>

      {/* Advanced theme selector (optional, hidden by default) */}
      <div className="hidden absolute right-0 mt-2 w-48 rounded-lg
                      bg-white dark:bg-neutral-900 
                      shadow-lg ring-1 ring-black ring-opacity-5
                      focus:outline-none"
           role="menu"
           aria-orientation="vertical">
        <div className="py-1" role="none">
          {themes.map((t) => (
            <button
              key={t.value}
              onClick={() => setTheme(t.value)}
              className={`flex w-full items-center px-4 py-2 text-sm
                         transition-colors duration-150
                         ${theme === t.value
                           ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-300'
                           : 'text-neutral-700 hover:bg-neutral-100 dark:text-neutral-300 dark:hover:bg-neutral-800'
                         }`}
              role="menuitem"
            >
              <span className="mr-3 text-base">{t.icon}</span>
              <span>{t.label}</span>
              {theme === t.value && (
                <svg className="ml-auto h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}