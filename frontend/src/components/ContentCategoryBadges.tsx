import React from 'react';

interface ContentCategoryBadgesProps {
  nativeType: string | null;
  extendedFormats: string[];
}

export const ContentCategoryBadges: React.FC<ContentCategoryBadgesProps> = ({
  nativeType,
  extendedFormats,
}) => {
  const getNativeTypeColor = (type: string) => {
    const colorMap: Record<string, string> = {
      'Reel': 'bg-pink-100 text-pink-800',
      'Post': 'bg-blue-100 text-blue-800',
      'Story': 'bg-purple-100 text-purple-800',
      'Video': 'bg-red-100 text-red-800',
      'Carousel': 'bg-orange-100 text-orange-800',
      'Guide': 'bg-teal-100 text-teal-800',
    };
    return colorMap[type] || 'bg-gray-100 text-gray-800';
  };

  const getFormatColor = () => 'bg-indigo-50 text-indigo-700 border border-indigo-200';

  if (!nativeType && !extendedFormats.length) return null;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Content Type</h3>

      <div className="flex flex-wrap gap-2">
        {/* Instagram Native Type */}
        {nativeType && (
          <div className={`inline-block rounded-full px-3 py-1 text-sm font-semibold ${getNativeTypeColor(nativeType)}`}>
            {nativeType}
          </div>
        )}

        {/* Extended Formats */}
        {extendedFormats.map((format) => (
          <div
            key={format}
            className={`inline-block rounded-full px-3 py-1 text-sm font-semibold ${getFormatColor()}`}
          >
            {format}
          </div>
        ))}
      </div>

      {extendedFormats.length > 0 && (
        <div className="mt-3 text-xs text-gray-500">
          Extended formats help understand content beyond native Instagram type
        </div>
      )}
    </div>
  );
};
