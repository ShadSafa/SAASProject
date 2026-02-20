import { useState, useEffect } from 'react';
import { getAnalysis } from '../api/analysis';
import type { Analysis } from '../types/analysis';

interface UseAnalysisResult {
  analysis: Analysis | null;
  loading: boolean;
  error: string | null;
  notAvailable: boolean; // 404 = analysis not yet generated
}

export function useAnalysis(viralPostId: number | null): UseAnalysisResult {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notAvailable, setNotAvailable] = useState(false);

  useEffect(() => {
    if (!viralPostId) return;

    setLoading(true);
    setError(null);
    setNotAvailable(false);

    getAnalysis(viralPostId)
      .then(data => {
        setAnalysis(data);
      })
      .catch(err => {
        if (err.response?.status === 404) {
          setNotAvailable(true);
        } else {
          setError(err.response?.data?.detail || 'Failed to load analysis');
        }
      })
      .finally(() => {
        setLoading(false);
      });
  }, [viralPostId]);

  return { analysis, loading, error, notAvailable };
}
