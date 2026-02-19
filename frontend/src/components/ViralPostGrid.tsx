import type { ViralPost } from '../types/scan';
import ViralPostCard from './ViralPostCard';

interface ViralPostGridProps {
  posts: ViralPost[];
  title?: string;
}

export default function ViralPostGrid({ posts, title }: ViralPostGridProps) {
  if (posts.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg font-medium">No results found</p>
        <p className="text-sm mt-1">Try a different time range or try again later</p>
      </div>
    );
  }

  return (
    <div>
      {title && (
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
          <span className="text-sm text-gray-500">{posts.length} posts found</span>
        </div>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {posts.map((post, index) => (
          <ViralPostCard key={post.id} post={post} rank={index + 1} />
        ))}
      </div>
    </div>
  );
}
