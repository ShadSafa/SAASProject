export type AccountStatus = 'active' | 'expired' | 'revoked';

export interface InstagramAccount {
  id: number;
  instagram_user_id: string;
  username: string;
  profile_picture: string | null;
  account_type: string | null;  // "Personal", "Creator", "Business"
  follower_count: number | null;
  status: AccountStatus;
  created_at: string;
}
