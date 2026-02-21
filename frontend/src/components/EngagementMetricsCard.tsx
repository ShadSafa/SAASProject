import React from 'react';

interface EngagementMetricsCardProps {
  engagementRate: number | null;
  followerCount: number;
  totalInteractions: number;
}

export const EngagementMetricsCard: React.FC<EngagementMetricsCardProps> = ({
  engagementRate,
  followerCount,
  totalInteractions,
}) => {
  const getEngagementColor = (rate: number) => {
    if (rate > 10) return 'text-green-600 bg-green-50';
    if (rate > 5) return 'text-blue-600 bg-blue-50';
    if (rate > 2) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">
        Engagement Metrics
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Engagement Rate */}
        <div className={`rounded-lg p-3 ${engagementRate !== null ? getEngagementColor(engagementRate) : 'bg-gray-50 text-gray-500'}`}>
          <div className="text-sm font-medium opacity-75">Engagement Rate</div>
          <div className="text-2xl font-bold">
            {engagementRate !== null ? `${engagementRate.toFixed(2)}%` : '—'}
          </div>
          <div className="text-xs opacity-60 mt-1">
            {engagementRate !== null && engagementRate > 5
              ? 'Excellent engagement'
              : 'Relative to followers'}
          </div>
        </div>

        {/* Total Interactions */}
        <div className="rounded-lg p-3 bg-purple-50 text-purple-600">
          <div className="text-sm font-medium opacity-75">Total Interactions</div>
          <div className="text-2xl font-bold">
            {totalInteractions.toLocaleString()}
          </div>
          <div className="text-xs opacity-60 mt-1">Likes + Comments + Saves + Shares</div>
        </div>

        {/* Follower Count */}
        <div className="rounded-lg p-3 bg-indigo-50 text-indigo-600">
          <div className="text-sm font-medium opacity-75">Creator Followers</div>
          <div className="text-2xl font-bold">
            {(followerCount / 1000).toFixed(0)}K
          </div>
          <div className="text-xs opacity-60 mt-1">Size reference</div>
        </div>
      </div>

      <div className="mt-3 text-xs text-gray-500">
        Engagement rate shows interaction volume relative to follower count. High rates indicate content resonates strongly with the audience.
      </div>
    </div>
  );
};
