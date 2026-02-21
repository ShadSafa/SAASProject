import { AlgorithmFactorBadge } from './AlgorithmFactorBadge';
import type { Analysis } from '../types/analysis';

interface AnalysisPanelProps {
  analysis: Analysis;
}

export function AnalysisPanel({ analysis }: AnalysisPanelProps) {
  return (
    <div className="mt-4 pt-4 border-t border-gray-200">
      {/* Why Viral Summary */}
      {analysis.why_viral_summary && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Why It Went Viral</h4>
          <p className="text-sm text-gray-700 leading-relaxed">{analysis.why_viral_summary}</p>
          {analysis.confidence_score && (
            <p className="text-xs text-gray-500 mt-1">
              Confidence: {(analysis.confidence_score * 100).toFixed(0)}%
            </p>
          )}
        </div>
      )}

      {/* Algorithm Factors */}
      <div className="space-y-2">
        <h4 className="text-sm font-semibold text-gray-900 mb-2">Algorithm Factors</h4>
        <div className="grid grid-cols-2 gap-2">
          <AlgorithmFactorBadge label="Hook Strength" score={analysis.hook_strength_score} />
          <AlgorithmFactorBadge label="Posting Time" score={analysis.posting_time_score} />
          <AlgorithmFactorBadge label="Eng. Velocity" score={analysis.engagement_velocity_score} />
          <AlgorithmFactorBadge label="Save/Share" score={analysis.save_share_ratio_score} />
          <AlgorithmFactorBadge label="Hashtag Perf." score={analysis.hashtag_performance_score} />
          <AlgorithmFactorBadge label="Audience Ret." score={analysis.audience_retention_score} />
        </div>

        {/* Emotional Trigger */}
        {analysis.emotional_trigger && (
          <div className="mt-2 px-3 py-2 bg-purple-50 rounded-md border border-purple-200">
            <span className="text-sm font-medium text-purple-900">
              Emotional Trigger: <span className="capitalize font-semibold">{analysis.emotional_trigger}</span>
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
