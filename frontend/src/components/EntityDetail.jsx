import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import api from '../services/api';
import RiskScoreCards from './RiskScoreCards';
import FraudRulesTable from './FraudRulesTable';
import NetworkConnectionsTable from './NetworkConnectionsTable';
import ClaimsTable from './ClaimsTable';
import CommunityAnalysisTable from './CommunityAnalysisTable';

function EntityDetail({ entity, onStatusUpdate }) {
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [updatingStatus, setUpdatingStatus] = useState(false);

  const loadEntityDetails = async (entityName) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.getEntityDetails(entityName);
      
      if (response.success) {
        setDetails(response.data);
      } else {
        setError('Failed to load entity details');
      }
    } catch (err) {
      setError('Error loading entity details');
      console.error('Error loading entity details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    if (!entity) return;
    
    try {
      setUpdatingStatus(true);
      const response = await api.updateEntityStatus(entity.entity_name, newStatus);
      
      if (response.success) {
        setDetails(prev => ({
          ...prev,
          entity: {
            ...prev.entity,
            investigation_status: newStatus
          }
        }));
        
        if (onStatusUpdate) {
          onStatusUpdate();
        }
      } else {
        setError('Failed to update status');
      }
    } catch (err) {
      setError('Error updating status');
      console.error('Error updating status:', err);
    } finally {
      setUpdatingStatus(false);
    }
  };

  useEffect(() => {
    if (entity) {
      loadEntityDetails(entity.entity_name);
    } else {
      setDetails(null);
    }
  }, [entity?.entity_name]);

  const getRiskColor = (score) => {
    if (score >= 85) return 'risk-high';
    if (score >= 70) return 'risk-medium';
    return 'risk-low';
  };

  if (!entity) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center text-gray-500">
          <p className="text-xl mb-2">Select an entity from the list</p>
          <p className="text-sm">Click on any entity to view their risk profile and network connections</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <Loader2 size={32} className="animate-spin text-lightblue-500 mx-auto mb-2" />
          <p className="text-sm text-gray-600">Loading entity details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 text-red-800 px-6 py-4 rounded">
          {error}
        </div>
      </div>
    );
  }

  if (!details) {
    return null;
  }

  return (
    <div className="flex-1 overflow-y-auto scrollable bg-gray-50">
      <div className="p-6">
        <div className="mb-6 pb-4 border-b border-silver-200">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-navy-800">{details.entity.entity_name}</h1>
              <p className="text-gray-600">{details.entity.entity_type}</p>
            </div>
            <div className="text-right">
              <div className={`text-3xl font-bold ${getRiskColor(details.entity.ensemble_score)}`}>
                {details.entity.ensemble_score.toFixed(1)}
              </div>
              <p className="text-sm text-gray-500">Ensemble Risk Score</p>
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Investigation Status:
            </label>
            <select
              value={details.entity.investigation_status}
              onChange={(e) => handleStatusChange(e.target.value)}
              disabled={updatingStatus}
              className="border border-silver-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-lightblue-500 disabled:opacity-50 transition-all duration-150"
            >
              <option value="Not Reviewed">Not Reviewed</option>
              <option value="Under Investigation">Under Investigation</option>
              <option value="Bad Actor">Bad Actor</option>
              <option value="Cleared">Cleared</option>
            </select>
          </div>
        </div>

        <RiskScoreCards entity={details.entity} />

        <FraudRulesTable rules={details.fraud_rules} />

        <NetworkConnectionsTable connections={details.connections} />

        <ClaimsTable claims={details.claims} />

        <CommunityAnalysisTable 
          communities={details.communities}
          communityMembers={details.community_members}
        />
      </div>
    </div>
  );
}

export default EntityDetail;