import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 bg-white dark:bg-gray-900">
      <div className="text-center max-w-md">
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
          Page Not Found
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          The page you&apos;re looking for doesn&apos;t exist.
        </p>
        <Link 
          href="/" 
          className="inline-block bg-blue-500 text-white hover:bg-blue-600 px-6 py-3 rounded-lg transition-colors"
        >
          Return Home
        </Link>
      </div>
    </div>
  )
}
