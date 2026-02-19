import { useScan } from '../hooks/useScan';
import ScanForm from '../components/ScanForm';
import ScanProgress from '../components/ScanProgress';
import ViralPostGrid from '../components/ViralPostGrid';
import type { TimeRange } from '../types/scan';

export default function ScanPage() {
  const {
    status,
    scanResults,
    isScanning,
    error,
    startScan,
    startUrlScan,
    clearResults,
  } = useScan();

  const handleStartScan = (timeRange: TimeRange) => {
    startScan(timeRange);
  };

  const handleAnalyzeUrl = (url: string) => {
    startUrlScan(url);
  };

  const isInProgress = status === 'pending' || status === 'running';

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Viral Content Discovery</h1>
        <p className="text-gray-500 mt-1">
          Find the top viral Instagram posts ranked by growth velocity
        </p>
      </div>

      {/* Scan form — always visible unless scanning */}
      {!isInProgress && (
        <ScanForm
          onStartScan={handleStartScan}
          onAnalyzeUrl={handleAnalyzeUrl}
          disabled={isScanning}
        />
      )}

      {/* Progress state */}
      {isInProgress && (
        <ScanProgress status={status as 'pending' | 'running'} />
      )}

      {/* Error state (SCAN-08) */}
      {status === 'failed' && error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-red-800 mb-1">Scan Failed</h3>
          <p className="text-sm text-red-700">{error}</p>
          <button
            onClick={clearResults}
            className="mt-3 px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Results — shown when completed with results */}
      {status === 'completed' && scanResults.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="bg-green-50 border border-green-200 rounded-lg px-4 py-2">
              <p className="text-sm font-medium text-green-800">
                Scan complete &mdash; found {scanResults.length} viral posts
              </p>
            </div>
            <button
              onClick={clearResults}
              className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
            >
              New Scan
            </button>
          </div>

          <ViralPostGrid
            posts={scanResults}
            title="Viral Posts by Growth Velocity"
          />
        </div>
      )}

      {/* Completed but no results */}
      {status === 'completed' && scanResults.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
          <p className="text-sm font-medium text-yellow-800">
            Scan completed but no viral posts were found for this time range.
          </p>
          <p className="text-xs text-yellow-700 mt-1">
            Try a wider time range (7d) or try again later.
          </p>
          <button
            onClick={clearResults}
            className="mt-3 px-4 py-2 text-sm bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  );
}
