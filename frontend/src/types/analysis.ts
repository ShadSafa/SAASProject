export interface Analysis {
  id: number;
  viral_post_id: number;
  why_viral_summary: string | null;
  posting_time_score: number | null;
  hook_strength_score: number | null;
  emotional_trigger: string | null;
  engagement_velocity_score: number | null;
  save_share_ratio_score: number | null;
  hashtag_performance_score: number | null;
  audience_retention_score: number | null;
  confidence_score: number | null;
  created_at: string;
}
