export default function SkeletonLoader() {
  return (
    <div className="animate-pulse space-y-2">
      <div className="h-3 rounded bg-gray-200" style={{ width: "80%" }} />
      <div className="h-3 rounded bg-gray-200" style={{ width: "90%" }} />
      <div className="h-3 rounded bg-gray-200" style={{ width: "75%" }} />
    </div>
  );
}

