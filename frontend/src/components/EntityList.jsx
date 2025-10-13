import { Loader2 } from 'lucide-react';

function EntityList({ entities, selectedEntity, onEntitySelect, loading, sortBy, onSortChange }) {
  const getRiskColor = (score) => {
    if (score >= 85) return 'risk-high';
    if (score >= 70) return 'risk-medium';
    return 'risk-low';
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'Bad Actor': return 'badge-red';
      case 'Under Investigation': return 'badge-yellow';
      case 'Cleared': return 'badge-green';
      default: return 'badge-gray';
    }
  };

  if (loading) {
    return (
      <div className="w-1/3 bg-white border-r border-silver-200 flex items-center justify-center">
        <div className="text-center">
          <Loader2 size={32} className="animate-spin text-lightblue-500 mx-auto mb-2" />
          <p className="text-sm text-gray-600">Loading entities...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-1/3 bg-white border-r border-silver-200 flex flex-col">
      <div className="p-4 border-b border-silver-200 bg-gray-50">
        <h2 className="font-bold text-lg text-navy-800">Co-Fraud Risk Rankings</h2>
        <div className="flex gap-2 mt-3">
          <button
            onClick={() => onSortChange('ensemble_score')}
            className={`px-3 py-1.5 rounded text-sm font-medium transition-colors duration-150 ${
              sortBy === 'ensemble_score'
                ? 'bg-lightblue-500 text-white'
                : 'bg-white border border-silver-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            Risk Score
          </button>
          <button
            onClick={() => onSortChange('total_exposure')}
            className={`px-3 py-1.5 rounded text-sm font-medium transition-colors duration-150 ${
              sortBy === 'total_exposure'
                ? 'bg-lightblue-500 text-white'
                : 'bg-white border border-silver-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            Exposure
          </button>
          <button
            onClick={() => onSortChange('connected_claims_count')}
            className={`px-3 py-1.5 rounded text-sm font-medium transition-colors duration-150 ${
              sortBy === 'connected_claims_count'
                ? 'bg-lightblue-500 text-white'
                : 'bg-white border border-silver-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            Claims
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto scrollable">
        {entities.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p>No entities match the current filters.</p>
          </div>
        ) : (
          <div className="divide-y divide-silver-200">
            {entities.map((entity) => (
              <div
                key={entity.entity_name}
                onClick={() => onEntitySelect(entity)}
                className={`p-4 cursor-pointer transition-all duration-150 border-l-4 ${
                  selectedEntity?.entity_name === entity.entity_name
                    ? 'bg-lightblue-50 border-lightblue-600'
                    : 'hover:bg-gray-50 border-transparent'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-semibold text-sm text-gray-900">{entity.entity_name}</div>
                    <div className="text-xs text-gray-600 mb-2">{entity.entity_type}</div>
                    <div className="flex items-center gap-4">
                      <div>
                        <span className={`text-xl font-bold ${getRiskColor(entity.ensemble_score)}`}>
                          {entity.ensemble_score.toFixed(0)}
                        </span>
                        <span className="text-xs text-gray-500 ml-1">risk</span>
                      </div>
                      <div className="text-xs text-gray-600">
                        {entity.connected_claims_count} claims
                      </div>
                      <div className="text-xs text-gray-600">
                        ${(entity.total_exposure / 1000).toFixed(0)}k
                      </div>
                    </div>
                  </div>
                  <div className="text-right ml-2">
                    <div className={`badge ${getStatusColor(entity.investigation_status)} text-xs mb-1`}>
                      {entity.investigation_status}
                    </div>
                    <div className="text-xs text-gray-500">#{entity.priority_rank}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default EntityList;