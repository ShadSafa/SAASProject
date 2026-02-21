import React, { useState } from 'react';

interface NicheBadgeProps {
  analysisId: number;  // NEW: needed for API call
  niche: string | null;  // AI-detected niche
  userNicheOverride: string | null;  // NEW: user override
  confidence: number | null;
  secondaryNiche?: string | null;
  reasoning?: string | null;
  onNicheUpdated?: (newNiche: string) => void;  // Callback after save
}

export const NicheBadge: React.FC<NicheBadgeProps> = ({
  analysisId,
  niche,
  userNicheOverride,
  confidence,
  secondaryNiche,
  reasoning,
  onNicheUpdated,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(userNicheOverride || niche || '');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Display effective niche (override if exists, else AI-detected)
  const effectiveNiche = userNicheOverride || niche;

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

  const handleSaveOverride = async () => {
    if (!editValue.trim()) {
      setError('Niche cannot be empty');
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/analysis/${analysisId}/niche-override`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            niche_override: editValue.trim()
          })
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to save niche override');
      }

      const result = await response.json();
      setIsEditing(false);
      onNicheUpdated?.(result.effective_niche);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error saving niche');
    } finally {
      setIsSaving(false);
    }
  };

  const handleClearOverride = async () => {
    setIsSaving(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/analysis/${analysisId}/niche-override`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ niche_override: null })
        }
      );

      if (!response.ok) throw new Error('Failed to clear niche override');

      setEditValue(niche || '');
      setIsEditing(false);
      onNicheUpdated?.(niche || '');

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error clearing override');
    } finally {
      setIsSaving(false);
    }
  };

  if (!effectiveNiche) return null;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Content Niche</h3>

      {isEditing ? (
        // Edit mode
        <div className="space-y-2">
          <div className="flex gap-2">
            <input
              type="text"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              placeholder="Enter niche..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isSaving}
            />
          </div>

          {error && <div className="text-sm text-red-600">{error}</div>}

          <div className="flex gap-2">
            <button
              onClick={handleSaveOverride}
              disabled={isSaving}
              className="px-3 py-1 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {isSaving ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={() => {
                setIsEditing(false);
                setEditValue(userNicheOverride || niche || '');
                setError(null);
              }}
              disabled={isSaving}
              className="px-3 py-1 bg-gray-300 text-gray-800 rounded text-sm font-medium hover:bg-gray-400 disabled:opacity-50"
            >
              Cancel
            </button>
            {userNicheOverride && (
              <button
                onClick={handleClearOverride}
                disabled={isSaving}
                className="px-3 py-1 bg-red-100 text-red-700 rounded text-sm font-medium hover:bg-red-200 disabled:opacity-50"
              >
                Clear Override
              </button>
            )}
          </div>
        </div>
      ) : (
        // Display mode
        <div className="flex flex-col gap-3">
          {/* Niche display */}
          <div
            onClick={() => setIsEditing(true)}
            className={`rounded-lg border p-3 flex items-start justify-between cursor-pointer hover:shadow-md transition ${
              userNicheOverride
                ? 'bg-purple-50 border-purple-300'
                : getConfidenceColor(confidence || 0.5)
            }`}
          >
            <div>
              <div className="font-semibold">{effectiveNiche}</div>
              {userNicheOverride && (
                <div className="text-xs text-purple-600 mt-1">User customized</div>
              )}
              {!userNicheOverride && reasoning && (
                <div className="text-sm opacity-80 mt-1">{reasoning}</div>
              )}
            </div>
            <div className="ml-2 text-right">
              <div className="text-xs font-semibold opacity-75">
                {userNicheOverride ? 'Custom' : 'Confidence'}
              </div>
              <div className="text-lg font-bold">
                {userNicheOverride ? '✓' : `${((confidence || 0) * 100).toFixed(0)}%`}
              </div>
            </div>
          </div>

          {/* Original AI niche if override exists */}
          {userNicheOverride && (
            <div className="rounded-lg border border-blue-300 p-2 bg-blue-50 text-blue-700">
              <div className="text-sm">
                <span className="font-semibold">AI detected:</span> {niche}
              </div>
            </div>
          )}

          {/* Secondary niche */}
          {secondaryNiche && !userNicheOverride && (
            <div className="rounded-lg border border-gray-300 p-2 bg-gray-50 text-gray-700">
              <div className="text-sm">
                <span className="font-semibold">Also fits:</span> {secondaryNiche}
              </div>
            </div>
          )}

          {/* Hint */}
          <div className="text-xs text-gray-500">
            {userNicheOverride
              ? 'Click to edit your custom niche'
              : 'Click to customize niche'}
          </div>
        </div>
      )}
    </div>
  );
};
