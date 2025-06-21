export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-500 border-r-transparent motion-reduce:animate-none" role="status">
          <span className="sr-only">Loading...</span>
        </div>
        <p className="mt-4 text-neutral-600 dark:text-neutral-400">
          Please wait while we prepare your session...
        </p>
      </div>
    </div>
  );
}