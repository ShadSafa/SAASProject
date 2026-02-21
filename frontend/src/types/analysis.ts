export interface AudienceDemographics {
  age_range?: {
    [key: string]: number;  // e.g., "18-24": 25
  };
  gender_distribution?: {
    [key: string]: number;  // e.g., "male": 40
  };
  top_countries?: Array<{
    code: string;  // ISO country code
    percentage: number;
  }>;
}

export interface AudienceInterests {
  inferred_topics?: string[];  // e.g., ["fitness", "wellness"]
  content_affinity?: string[];  // e.g., ["educational", "inspirational"]
  hashtag_analysis?: string[];
  inferred_formats?: string[];  // Extended content formats from Phase 05-03
  categorization_confidence?: number;
  categorization_reason?: string;
  niche?: string;  // Primary niche from Phase 05-05
  niche_secondary?: string | null;
  niche_confidence?: number;
  niche_reasoning?: string;
  niche_keywords?: string[];
}

export interface Analysis {
  id: number;
  viral_post_id: number;

  // Phase 04: OpenAI Analysis
  why_viral_summary: string | null;
  posting_time_score: number | null;
  hook_strength_score: number | null;
  emotional_trigger: string | null;
  engagement_velocity_score: number | null;
  save_share_ratio_score: number | null;
  hashtag_performance_score: number | null;
  audience_retention_score: number | null;
  confidence_score: number | null;

  // Phase 05: Enriched Data
  engagement_rate?: number | null;  // Percentage (0-100+)
  content_category?: string | null;  // Instagram native type (Reel, Post, etc.)
  niche?: string | null;  // Detected niche
  audience_demographics?: AudienceDemographics | null;
  audience_interests?: AudienceInterests | null;
  user_niche_override?: string | null;  // User-customized niche (overrides AI-detected niche)

  created_at: string;
  updated_at?: string;
}
