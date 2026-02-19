import type { ViralPost } from '../types/scan';

interface ViralPostCardProps {
  post: ViralPost;
  rank: number;
}

function formatNumber(n: number | null): string {
  if (n === null || n === undefined) return '\u2014';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

function getScoreColor(score: number | null): string {
  if (score === null) return 'text-gray-500 bg-gray-50';
  if (score >= 80) return 'text-green-700 bg-green-50 border-green-200';
  if (score >= 60) return 'text-blue-700 bg-blue-50 border-blue-200';
  if (score >= 30) return 'text-yellow-700 bg-yellow-50 border-yellow-200';
  return 'text-red-700 bg-red-50 border-red-200';
}

function getScoreLabel(score: number | null): string {
  if (score === null) return '\u2014';
  if (score >= 80) return 'Exceptional';
  if (score >= 60) return 'High';
  if (score >= 30) return 'Moderate';
  return 'Low';
}

export default function ViralPostCard({ post, rank }: ViralPostCardProps) {
  const totalEngagement =
    (post.engagement.likes || 0) +
    (post.engagement.comments || 0) +
    (post.engagement.saves || 0) +
    (post.engagement.shares || 0);

  const scoreColor = getScoreColor(post.viral_score);
  const scoreLabel = getScoreLabel(post.viral_score);

  // Use S3 thumbnail (persistent); fall back to Instagram thumbnail URL
  const thumbSrc = post.thumbnail_url;

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-md transition-shadow group">
      {/* Thumbnail */}
      <div className="relative">
        {thumbSrc ? (
          <a href={post.instagram_url || '#'} target="_blank" rel="noopener noreferrer">
            <img
              src={thumbSrc}
              alt={`Post by @${post.creator_username || 'unknown'}`}
              className="w-full h-48 object-cover group-hover:opacity-95 transition-opacity"
              loading="lazy"
              onError={(e) => {
                // If thumbnail fails to load, show placeholder
                (e.target as HTMLImageElement).style.display = 'none';
                (e.target as HTMLImageElement).parentElement!.classList.add('bg-gray-100');
              }}
            />
          </a>
        ) : (
          <div className="w-full h-48 bg-gray-100 flex items-center justify-center">
            <span className="text-gray-400 text-sm">No preview</span>
          </div>
        )}

        {/* Rank badge */}
        <div className="absolute top-2 left-2 bg-black/70 text-white text-xs font-bold px-2 py-1 rounded-full">
          #{rank}
        </div>

        {/* Post type badge */}
        {post.post_type && (
          <div className="absolute top-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded-full capitalize">
            {post.post_type}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Creator info */}
        <div>
          <p className="text-sm font-semibold text-gray-900 truncate">
            @{post.creator_username || 'unknown'}
          </p>
          {post.creator_follower_count !== null && (
            <p className="text-xs text-gray-500">
              {formatNumber(post.creator_follower_count)} followers
            </p>
          )}
        </div>

        {/* Engagement metrics */}
        <div className="grid grid-cols-2 gap-1 text-xs text-gray-600">
          <div className="flex items-center gap-1">
            <span>Likes:</span>
            <span className="font-medium text-gray-900">{formatNumber(post.engagement.likes)}</span>
          </div>
          <div className="flex items-center gap-1">
            <span>Comments:</span>
            <span className="font-medium text-gray-900">{formatNumber(post.engagement.comments)}</span>
          </div>
          {post.engagement.saves > 0 && (
            <div className="flex items-center gap-1">
              <span>Saves:</span>
              <span className="font-medium text-gray-900">{formatNumber(post.engagement.saves)}</span>
            </div>
          )}
          <div className="flex items-center gap-1">
            <span>Total:</span>
            <span className="font-medium text-gray-900">{formatNumber(totalEngagement)}</span>
          </div>
        </div>

        {/* Viral score */}
        <div className={`flex items-center justify-between px-3 py-2 rounded-lg border ${scoreColor}`}>
          <span className="text-xs font-medium">{scoreLabel} Viral</span>
          <span className="text-sm font-bold">
            {post.viral_score !== null ? `${Math.round(post.viral_score)}/100` : '\u2014'}
          </span>
        </div>

        {/* View post link */}
        {post.instagram_url && (
          <a
            href={post.instagram_url}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full text-center py-2 text-sm text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors"
          >
            View on Instagram
          </a>
        )}
      </div>
    </div>
  );
}
