function RiskScoreCards({ entity }) {
  return (
    <div className="mb-6">
      <h3 className="text-lg font-semibold text-navy-800 mb-3">Risk Score Breakdown</h3>
      
      <div className="grid grid-cols-7 gap-2">
        <div className="card p-4 text-center h-20 flex flex-col justify-center">
          <div className="text-2xl font-bold text-red-600 mb-1">
            {entity.ensemble_score.toFixed(1)}
          </div>
          <div className="text-xs text-gray-600 uppercase tracking-wide leading-tight">
            Ensemble Score
          </div>
        </div>

        <div className="card p-4 text-center h-20 flex flex-col justify-center">
          <div className="text-2xl font-bold text-blue-600 mb-1">
            {entity.social_network_score.toFixed(1)}
          </div>
          <div className="text-xs text-gray-600 uppercase tracking-wide leading-tight">
            Network Score
          </div>
        </div>

        <div className="card p-4 text-center h-20 flex flex-col justify-center">
          <div className="text-2xl font-bold text-orange-600 mb-1">
            {(entity.composite_external_score * 20).toFixed(1)}
          </div>
          <div className="text-xs text-gray-600 uppercase tracking-wide leading-tight">
            External Score
          </div>
        </div>

        <div className="card p-4 text-center h-20 flex flex-col justify-center">
          <div className="text-2xl font-bold text-purple-600 mb-1">
            {entity.connected_claims_count}
          </div>
          <div className="text-xs text-gray-600 uppercase tracking-wide leading-tight">
            Assoc. Claims
          </div>
        </div>

        <div className="card p-4 text-center h-20 flex flex-col justify-center">
          <div className="text-2xl font-bold text-green-600 mb-1">
            ${(entity.total_exposure / 1000).toFixed(0)}k
          </div>
          <div className="text-xs text-gray-600 uppercase tracking-wide leading-tight">
            Total Reserves
          </div>
        </div>

        <div className="card p-4 text-center h-20 flex flex-col justify-center">
          <div className="text-2xl font-bold text-yellow-600 mb-1">
            {(entity.max_external_fraud_score * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-600 uppercase tracking-wide leading-tight">
            Max Assoc. Ext
          </div>
        </div>

        <div className="card p-4 text-center h-20 flex flex-col justify-center">
          <div className="text-2xl font-bold text-indigo-600 mb-1">
            {(entity.avg_external_fraud_score * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-600 uppercase tracking-wide leading-tight">
            Avg Assoc. Ext
          </div>
        </div>
      </div>
    </div>
  );
}

export default RiskScoreCards;