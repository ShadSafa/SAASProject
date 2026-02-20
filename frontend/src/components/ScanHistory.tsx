import { useEffect, useState } from 'react';
import { api } from '../utils/api';

interface ScanHistoryItem {
  scan_id: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  scan_type: 'hashtag' | 'url';
  time_range?: string;
  created_at: string;
  completed_at?: string;
  post_count: number;
}

export default function ScanHistory() {
  const [scans, setScans] = useState<ScanHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchScanHistory();
  }, []);

  const fetchScanHistory = async () => {
    try {
      setLoading(true);
      const response = await api.get('/scans/history');
      setScans(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load scan history');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, string> = {
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800',
      running: 'bg-blue-100 text-blue-800',
    };

    return statusColors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Loading scan history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
      </div>
    );
  }

  if (scans.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No scans yet. Start a scan from the Scan tab.</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Scans</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Type</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Time Range</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Status</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Posts Found</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Created</th>
            </tr>
          </thead>
          <tbody>
            {scans.map((scan) => (
              <tr key={scan.scan_id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4 text-sm text-gray-900">
                  <span className="capitalize">{scan.scan_type}</span>
                </td>
                <td className="py-3 px-4 text-sm text-gray-600">
                  {scan.time_range || '-'}
                </td>
                <td className="py-3 px-4 text-sm">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusBadge(scan.status)}`}>
                    {scan.status}
                  </span>
                </td>
                <td className="py-3 px-4 text-sm text-gray-900">{scan.post_count}</td>
                <td className="py-3 px-4 text-sm text-gray-600">{formatDate(scan.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
