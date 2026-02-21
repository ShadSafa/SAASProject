interface AlgorithmFactorBadgeProps {
  label: string;
  score: number | null | undefined;
}

export function AlgorithmFactorBadge({ label, score }: AlgorithmFactorBadgeProps) {
  if (score === null || score === undefined) {
    return (
      <div className="flex items-center justify-between gap-2 px-3 py-2 bg-gray-100 rounded-md">
        <span className="text-xs font-medium text-gray-700 truncate">{label}</span>
        <span className="text-xs font-medium text-gray-500 whitespace-nowrap">N/A</span>
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
    <div className={`flex items-center justify-between gap-2 px-3 py-2 rounded-md ${colorClass}`}>
      <span className="text-xs font-medium truncate">{label}</span>
      <span className="text-sm font-bold whitespace-nowrap">{score.toFixed(0)}</span>
    </div>
  );
}
