import React from 'react';

interface NicheBadgeProps {
  niche: string | null;
  confidence: number | null;
  secondaryNiche?: string | null;
  reasoning?: string | null;
}

export const NicheBadge: React.FC<NicheBadgeProps> = ({
  niche,
  confidence,
  secondaryNiche,
  reasoning,
}) => {
  const getConfidenceColor = (conf: number) => {
    if (conf > 0.85) return 'bg-green-100 text-green-800 border-green-300';
    if (conf > 0.70) return 'bg-blue-100 text-blue-800 border-blue-300';
    if (conf > 0.50) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getConfidenceLabel = (conf: number) => {
    if (conf > 0.85) return 'Very High';
    if (conf > 0.70) return 'High';
    if (conf > 0.50) return 'Medium';
    return 'Low';
  };

  if (!niche) return null;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Content Niche</h3>

      <div className="flex flex-col gap-3">
        {/* Primary Niche */}
        <div className={`rounded-lg border p-3 flex items-start justify-between ${getConfidenceColor(confidence || 0.5)}`}>
          <div>
            <div className="font-semibold">{niche}</div>
            {reasoning && <div className="text-sm opacity-80 mt-1">{reasoning}</div>}
          </div>
          <div className="ml-2 text-right">
            <div className="text-xs font-semibold opacity-75">Confidence</div>
            <div className="text-lg font-bold">{((confidence || 0) * 100).toFixed(0)}%</div>
          </div>
        </div>

        {/* Secondary Niche */}
        {secondaryNiche && (
          <div className="rounded-lg border border-gray-300 p-2 bg-gray-50 text-gray-700">
            <div className="text-sm">
              <span className="font-semibold">Also fits:</span> {secondaryNiche}
            </div>
          </div>
        )}

        {/* Confidence Indicator */}
        <div className="text-xs text-gray-500">
          AI detected this niche with {getConfidenceLabel(confidence || 0.5).toLowerCase()} confidence
        </div>
      </div>
    </div>
  );
};
