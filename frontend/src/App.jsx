import { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import FilterBar from './components/FilterBar';
import EntityList from './components/EntityList';
import EntityDetail from './components/EntityDetail';
import api from './services/api';

function App() {
  const [entities, setEntities] = useState([]);
  const [filteredEntities, setFilteredEntities] = useState([]);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    sort_by: 'ensemble_score',
    filter_status: 'all',
    min_risk_score: 0,
    entity_type: 'All Types',
    search: ''
  });
  const [refreshing, setRefreshing] = useState(false);

  const applyClientSideFilters = (entitiesList, currentFilters) => {
    let filtered = [...entitiesList];
    
    // Apply search filter
    if (currentFilters.search && currentFilters.search.trim()) {
      const searchLower = currentFilters.search.toLowerCase();
      filtered = filtered.filter(entity => 
        entity.entity_name.toLowerCase().includes(searchLower)
      );
    }
    
    return filtered;
  };

  const loadEntities = async (currentFilters = filters) => {
    try {
      setLoading(true);
      setError(null);
      
      const filterParams = {};
      if (currentFilters.sort_by) filterParams.sort_by = currentFilters.sort_by;
      if (currentFilters.filter_status && currentFilters.filter_status !== 'all') {
        filterParams.filter_status = currentFilters.filter_status;
      }
      if (currentFilters.min_risk_score > 0) {
        filterParams.min_risk_score = currentFilters.min_risk_score;
      }
      if (currentFilters.entity_type && currentFilters.entity_type !== 'All Types') {
        filterParams.entity_type = currentFilters.entity_type;
      }

      const response = await api.getEntities(filterParams);
      
      if (response.success) {
        setEntities(response.data);
        const clientFiltered = applyClientSideFilters(response.data, currentFilters);
        setFilteredEntities(clientFiltered);
        
        if (selectedEntity && response.data.length > 0) {
          const updatedEntity = response.data.find(
            e => e.entity_name === selectedEntity.entity_name
          );
          if (updatedEntity) {
            setSelectedEntity(updatedEntity);
          } else {
            setSelectedEntity(null);
          }
        }
      } else {
        setError('Failed to load entities');
      }
    } catch (err) {
      setError('Error connecting to server');
      console.error('Error loading entities:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await api.reloadData();
      await loadEntities();
    } catch (err) {
      setError('Failed to refresh data');
      console.error('Error refreshing:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    // Reload from server for all filters except search
    loadEntities(newFilters);
  };

  // Apply search filter whenever entities change
  useEffect(() => {
    if (entities.length > 0) {
      const clientFiltered = applyClientSideFilters(entities, filters);
      setFilteredEntities(clientFiltered);
    }
  }, [entities, filters.search]);

  const handleEntitySelect = (entity) => {
    setSelectedEntity(entity);
  };

  const handleStatusUpdate = async () => {
    await loadEntities();
    if (selectedEntity) {
      try {
        const response = await api.getEntityDetails(selectedEntity.entity_name);
        if (response.success) {
          setSelectedEntity({
            ...selectedEntity,
            investigation_status: response.data.entity.investigation_status
          });
        }
      } catch (err) {
        console.error('Error updating selected entity:', err);
      }
    }
  };

  useEffect(() => {
    loadEntities();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-navy-800 text-white shadow-lg">
        <div className="px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Fraud Hub - Fraud Detection Dashboard</h1>
            <p className="text-sm text-lightblue-400">AI-Powered Network Analysis Software Suite</p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="bg-lightblue-500 hover:bg-lightblue-600 text-white px-4 py-2 rounded font-medium transition-colors duration-150 flex items-center gap-2 disabled:opacity-50"
          >
            <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
            Refresh Data
          </button>
        </div>
      </header>

      <FilterBar filters={filters} onFilterChange={handleFilterChange} />

      {error && (
        <div className="mx-6 mt-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="flex h-[calc(100vh-180px)]">
        <EntityList
          entities={filteredEntities}
          selectedEntity={selectedEntity}
          onEntitySelect={handleEntitySelect}
          loading={loading}
          sortBy={filters.sort_by}
          onSortChange={(sort) => handleFilterChange({ ...filters, sort_by: sort })}
        />

        <EntityDetail
          entity={selectedEntity}
          onStatusUpdate={handleStatusUpdate}
          onEntitySelect={handleEntitySelect}
          sortBy={filters.sort_by}
        />
      </div>
    </div>
  );
}

export default App;