import LoadingSpinner from '@/components/ui/LoadingSpinner'

export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center space-y-4">
        <LoadingSpinner 
          size="lg" 
          variant="inline" 
          label="Please wait while we prepare your session..."
          showLabel={true}
        />
      </div>
    </div>
  );
}