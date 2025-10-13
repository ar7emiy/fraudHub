import { useState } from 'react';
import { Search } from 'lucide-react';

function FilterBar({ filters, onFilterChange }) {
  const [localFilters, setLocalFilters] = useState(filters);

  const handleChange = (key, value) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  return (
    <div className="bg-white border-b border-silver-200 shadow-sm">
      <div className="px-6 py-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2 flex-1 max-w-xs">
            <Search size={16} className="text-gray-400" />
            <input
              type="text"
              placeholder="Search entity name..."
              value={localFilters.search || ''}
              onChange={(e) => handleChange('search', e.target.value)}
              className="flex-1 border border-silver-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-lightblue-500 transition-all duration-150"
            />
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Entity Type:</label>
            <select
              value={localFilters.entity_type}
              onChange={(e) => handleChange('entity_type', e.target.value)}
              className="border border-silver-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-lightblue-500 transition-all duration-150"
            >
              <option>All Types</option>
              <option>Doctor</option>
              <option>Lawyer</option>
              <option>Business</option>
              <option>Regular Person</option>
              <option>Driver</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Min Risk Score:</label>
            <input
              type="range"
              min="0"
              max="100"
              value={localFilters.min_risk_score}
              onChange={(e) => handleChange('min_risk_score', parseInt(e.target.value))}
              className="w-24"
            />
            <span className="text-sm font-medium text-gray-700 min-w-[2rem]">
              {localFilters.min_risk_score}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Status:</label>
            <select
              value={localFilters.filter_status}
              onChange={(e) => handleChange('filter_status', e.target.value)}
              className="border border-silver-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-lightblue-500 transition-all duration-150"
            >
              <option value="all">All</option>
              <option value="Not Reviewed">Not Reviewed</option>
              <option value="Under Investigation">Under Investigation</option>
              <option value="Bad Actor">Bad Actor</option>
              <option value="Cleared">Cleared</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FilterBar;