interface AlgorithmFactorBadgeProps {
  label: string;
  score: number | null | undefined;
}

export function AlgorithmFactorBadge({ label, score }: AlgorithmFactorBadgeProps) {
  if (score === null || score === undefined) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-xs text-gray-500">N/A</span>
      </div>
    );
  }

  // Color coding: red <40, yellow 40-70, green >70
  let colorClass = 'bg-red-100 text-red-700';
  if (score >= 70) {
    colorClass = 'bg-green-100 text-green-700';
  } else if (score >= 40) {
    colorClass = 'bg-yellow-100 text-yellow-700';
  }

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${colorClass}`}>
      <span className="text-sm font-medium">{label}</span>
      <span className="text-sm font-bold">{score.toFixed(0)}/100</span>
    </div>
  );
}
