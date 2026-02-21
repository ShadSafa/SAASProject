import { AlgorithmFactorBadge } from './AlgorithmFactorBadge';
import type { Analysis } from '../types/analysis';

interface AnalysisPanelProps {
  analysis: Analysis;
}

export function AnalysisPanel({ analysis }: AnalysisPanelProps) {
  return (
    <div className="mt-6 pt-6 border-t-2 border-gray-200">
      {/* Why Viral Summary */}
      {analysis.why_viral_summary && (
        <div className="mb-6">
          <h4 className="text-lg font-bold text-gray-900 mb-3">Why It Went Viral</h4>
          <p className="text-base text-gray-700 leading-relaxed">{analysis.why_viral_summary}</p>
          {analysis.confidence_score && (
            <p className="text-sm text-gray-500 mt-2">
              Confidence: {(analysis.confidence_score * 100).toFixed(0)}%
            </p>
          )}
        </div>
      )}

      {/* Algorithm Factors */}
      <div className="space-y-3">
        <h4 className="text-lg font-bold text-gray-900 mb-4">Algorithm Factors</h4>
        <div className="grid grid-cols-2 gap-3">
          <AlgorithmFactorBadge label="Hook Strength" score={analysis.hook_strength_score} />
          <AlgorithmFactorBadge label="Posting Time" score={analysis.posting_time_score} />
          <AlgorithmFactorBadge label="Engagement Velocity" score={analysis.engagement_velocity_score} />
          <AlgorithmFactorBadge label="Save/Share Ratio" score={analysis.save_share_ratio_score} />
          <AlgorithmFactorBadge label="Hashtag Performance" score={analysis.hashtag_performance_score} />
          <AlgorithmFactorBadge label="Audience Retention" score={analysis.audience_retention_score} />
        </div>

        {/* Emotional Trigger */}
        {analysis.emotional_trigger && (
          <div className="mt-4 px-4 py-3 bg-purple-50 rounded-lg border border-purple-200">
            <span className="text-base font-semibold text-purple-900">
              Emotional Trigger: <span className="capitalize font-bold">{analysis.emotional_trigger}</span>
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
