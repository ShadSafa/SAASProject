interface ScanProgressProps {
  status: 'pending' | 'running';
}

export default function ScanProgress({ status }: ScanProgressProps) {
  const statusMessages = {
    pending: { primary: 'Connecting to Instagram data sources...', secondary: 'Setting up your scan' },
    running: { primary: 'Analyzing viral content...', secondary: 'Calculating growth velocity for each post' },
  };

  const message = statusMessages[status];

  // Animated progress bar (indeterminate)
  const progressPercent = status === 'pending' ? 25 : 65;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
      <div className="text-center mb-6">
        <h2 className="text-lg font-semibold text-gray-900">{message.primary}</h2>
        <p className="text-sm text-gray-500 mt-1">{message.secondary}</p>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-8">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-1000"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Skeleton card grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 8 }, (_, i) => (
          <div key={i} className="rounded-xl border border-gray-100 overflow-hidden animate-pulse">
            {/* Thumbnail skeleton */}
            <div className="bg-gray-200 h-48 w-full" />
            <div className="p-3 space-y-2">
              <div className="bg-gray-200 h-3 rounded w-3/4" />
              <div className="bg-gray-200 h-3 rounded w-1/2" />
              <div className="bg-gray-200 h-3 rounded w-2/3" />
              <div className="bg-gray-200 h-6 rounded w-full mt-2" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
