import { AlgorithmFactorBadge } from './AlgorithmFactorBadge';
import { EngagementMetricsCard } from './EngagementMetricsCard';
import { ContentCategoryBadges } from './ContentCategoryBadges';
import { NicheBadge } from './NicheBadge';
import type { Analysis } from '../types/analysis';
import type { ViralPost } from '../types/scan';

interface AnalysisPanelProps {
  analysis: Analysis;
  viralPost?: ViralPost;
}

export function AnalysisPanel({ analysis, viralPost }: AnalysisPanelProps) {
  return (
    <div className="mt-4 pt-4 border-t border-gray-200">
      {/* Phase 05: Enriched Analysis Data */}

      {/* Engagement Metrics */}
      {analysis.engagement_rate !== null && analysis.engagement_rate !== undefined && viralPost && (
        <EngagementMetricsCard
          engagementRate={analysis.engagement_rate}
          followerCount={viralPost.creator_follower_count ?? 0}
          totalInteractions={
            (viralPost.engagement.likes ?? 0) +
            (viralPost.engagement.comments ?? 0) +
            (viralPost.engagement.saves ?? 0) +
            (viralPost.engagement.shares ?? 0)
          }
        />
      )}

      {/* Content Type & Niche */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ContentCategoryBadges
          nativeType={analysis.content_category || null}
          extendedFormats={
            analysis.audience_interests?.inferred_formats || []
          }
        />

        <NicheBadge
          niche={analysis.niche || null}
          confidence={analysis.audience_interests?.niche_confidence || null}
          secondaryNiche={analysis.audience_interests?.niche_secondary || null}
          reasoning={analysis.audience_interests?.niche_reasoning || null}
        />
      </div>

      {/* Audience Demographics (if available) */}
      {analysis.audience_demographics && Object.keys(analysis.audience_demographics).length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Audience Demographics
          </h3>

          <div className="space-y-4">
            {/* Age Distribution */}
            {analysis.audience_demographics.age_range && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Age Range</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {Object.entries(analysis.audience_demographics.age_range).map(([range, percentage]: [string, any]) => (
                    <div key={range} className="bg-blue-50 rounded p-2 text-center">
                      <div className="text-xs text-gray-600">{range}</div>
                      <div className="text-lg font-bold text-blue-600">{percentage}%</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Gender Distribution */}
            {analysis.audience_demographics.gender_distribution && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Gender</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {Object.entries(analysis.audience_demographics.gender_distribution).map(([gender, percentage]: [string, any]) => (
                    <div key={gender} className="bg-purple-50 rounded p-2 text-center">
                      <div className="text-xs text-gray-600 capitalize">{gender}</div>
                      <div className="text-lg font-bold text-purple-600">{percentage}%</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Top Countries */}
            {analysis.audience_demographics.top_countries && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Top Locations</h4>
                <div className="space-y-1">
                  {analysis.audience_demographics.top_countries.map((country: any) => (
                    <div key={country.code} className="flex justify-between items-center text-sm">
                      <span className="text-gray-700">{country.code}</span>
                      <div className="w-24 h-2 bg-gray-200 rounded overflow-hidden">
                        <div
                          className="h-full bg-green-500"
                          style={{ width: `${country.percentage}%` }}
                        />
                      </div>
                      <span className="text-gray-600 font-semibold">{country.percentage}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Phase 04: OpenAI Analysis */}

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
