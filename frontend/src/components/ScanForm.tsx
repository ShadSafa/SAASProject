import { useState } from 'react';
import type { TimeRange } from '../types/scan';

interface ScanFormProps {
  onStartScan: (timeRange: TimeRange) => void;
  onAnalyzeUrl: (url: string) => void;
  disabled: boolean;
}

const TIME_RANGES: { value: TimeRange; label: string; description: string }[] = [
  { value: '12h', label: '12 Hours', description: 'Last 12 hours' },
  { value: '24h', label: '24 Hours', description: 'Last 24 hours' },
  { value: '48h', label: '48 Hours', description: 'Last 2 days' },
  { value: '7d',  label: '7 Days',   description: 'Last week' },
];

type Tab = 'discover' | 'analyze';

export default function ScanForm({ onStartScan, onAnalyzeUrl, disabled }: ScanFormProps) {
  const [activeTab, setActiveTab] = useState<Tab>('discover');
  const [selectedRange, setSelectedRange] = useState<TimeRange>('24h');
  const [urlInput, setUrlInput] = useState('');
  const [urlError, setUrlError] = useState('');

  const handleDiscover = () => {
    onStartScan(selectedRange);
  };

  const handleAnalyzeUrl = () => {
    setUrlError('');
    const trimmed = urlInput.trim();
    if (!trimmed) {
      setUrlError('Please enter an Instagram URL');
      return;
    }
    if (!trimmed.includes('instagram.com')) {
      setUrlError('URL must be an Instagram post URL (instagram.com/p/... or /reel/...)');
      return;
    }
    onAnalyzeUrl(trimmed);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      {/* Tab switcher */}
      <div className="flex space-x-1 mb-6 bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setActiveTab('discover')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'discover'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Discover Viral Posts
        </button>
        <button
          onClick={() => setActiveTab('analyze')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'analyze'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Analyze Specific Post
        </button>
      </div>

      {activeTab === 'discover' ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time Range
            </label>
            <div className="grid grid-cols-4 gap-2">
              {TIME_RANGES.map((range) => (
                <button
                  key={range.value}
                  onClick={() => setSelectedRange(range.value)}
                  className={`py-2 px-3 rounded-lg border text-sm font-medium transition-colors ${
                    selectedRange === range.value
                      ? 'border-blue-600 bg-blue-50 text-blue-700'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                  }`}
                >
                  <div className="font-semibold">{range.label}</div>
                  <div className="text-xs opacity-70">{range.description}</div>
                </button>
              ))}
            </div>
          </div>

          <p className="text-sm text-gray-500">
            Discover the top 20 viral Instagram posts from the last {selectedRange} ranked by growth velocity.
          </p>

          <button
            onClick={handleDiscover}
            disabled={disabled}
            className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {disabled ? 'Scanning...' : 'Start Discovery Scan'}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Instagram Post URL
            </label>
            <input
              type="url"
              value={urlInput}
              onChange={(e) => { setUrlInput(e.target.value); setUrlError(''); }}
              placeholder="https://www.instagram.com/p/SHORTCODE/"
              className={`w-full px-4 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                urlError ? 'border-red-400' : 'border-gray-300'
              }`}
            />
            {urlError && (
              <p className="mt-1 text-sm text-red-600">{urlError}</p>
            )}
          </div>

          <p className="text-sm text-gray-500">
            Analyze any public Instagram post, reel, or video to see its viral score and engagement breakdown.
          </p>

          <button
            onClick={handleAnalyzeUrl}
            disabled={disabled}
            className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {disabled ? 'Analyzing...' : 'Analyze Post'}
          </button>
        </div>
      )}
    </div>
  );
}
