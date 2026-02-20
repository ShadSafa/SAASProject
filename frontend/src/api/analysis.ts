import { api } from '../utils/api';
import type { Analysis } from '../types/analysis';

/**
 * Fetch analysis results for a viral post
 * @throws 404 if analysis not yet available
 * @throws 403 if not authorized
 */
export async function getAnalysis(viralPostId: number): Promise<Analysis> {
  const response = await api.get<Analysis>(`/api/analysis/${viralPostId}`);
  return response.data;
}

/**
 * Check if analysis exists (doesn't throw on 404)
 */
export async function hasAnalysis(viralPostId: number): Promise<boolean> {
  try {
    await getAnalysis(viralPostId);
    return true;
  } catch (error: any) {
    if (error.response?.status === 404) {
      return false;
    }
    throw error; // Re-throw non-404 errors
  }
}
