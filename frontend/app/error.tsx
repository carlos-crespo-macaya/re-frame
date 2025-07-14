'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service in production
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="text-center max-w-md">
        <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
          Something went wrong
        </h2>
        <p className="text-neutral-600 dark:text-neutral-400 mb-8">
          We apologize for the inconvenience. This error has been logged and we&apos;ll look into it.
        </p>
        <div className="space-y-4">
          <button
            onClick={reset}
            className="btn-base bg-primary-500 text-white hover:bg-primary-600 px-6 py-3 rounded-lg"
          >
            Try again
          </button>
          <div>
            <a
              href="/"
              className="text-primary-500 hover:text-primary-600 underline"
            >
              Return to home
            </a>
          </div>
        </div>
        {process.env.NODE_ENV === 'development' && (
          <details className="mt-8 text-left">
            <summary className="cursor-pointer text-neutral-500">
              Error details (development only)
            </summary>
            <pre className="mt-2 whitespace-pre-wrap text-xs bg-neutral-100 dark:bg-neutral-800 p-4 rounded overflow-auto">
              {error.message}
              {error.stack}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}