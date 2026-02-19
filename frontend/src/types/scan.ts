export type ScanStatus = 'pending' | 'running' | 'completed' | 'failed';
export type ScanType = 'hashtag' | 'url';
export type TimeRange = '12h' | '24h' | '48h' | '7d';

export interface EngagementMetrics {
  likes: number;
  comments: number;
  saves: number;
  shares: number;
}

export interface ViralPost {
  id: number;
  instagram_post_id: string;
  instagram_url: string | null;
  post_type: string | null;
  thumbnail_url: string | null;
  creator_username: string | null;
  creator_follower_count: number | null;
  engagement: EngagementMetrics;
  viral_score: number | null;
  post_age_hours: number | null;
}

export interface ScanTriggerResponse {
  scan_id: number;
  status: ScanStatus;
  message: string;
}

export interface ScanResponse {
  scan_id: number;
  status: ScanStatus;
  scan_type: ScanType;
  time_range: TimeRange | null;
  target_url: string | null;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
  results: ViralPost[];
}

export interface ScanHistoryItem {
  scan_id: number;
  status: ScanStatus;
  scan_type: ScanType;
  time_range: TimeRange | null;
  created_at: string;
  completed_at: string | null;
  post_count: number;
}
