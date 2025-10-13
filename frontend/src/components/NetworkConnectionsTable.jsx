function NetworkConnectionsTable({ connections }) {
    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-navy-800 mb-3">Network Connections</h3>
        <div className="table-container">
          <div className="max-h-64 overflow-y-auto scrollable">
            <table className="w-full">
              <thead className="table-header">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Connected Entity
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    <div className="flex items-center justify-center gap-1">
                      Strength
                      <div className="relative group">
                        <span className="text-gray-400 hover:text-gray-600 cursor-help text-xs">?</span>
                        <div className="absolute left-full top-1/2 transform -translate-y-1/2 ml-2 px-3 py-2 bg-gray-800 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-[9999]">
                          Number of times entities appear together on claims
                          <div className="absolute top-1/2 left-0 transform -translate-y-1/2 -translate-x-full border-4 border-transparent border-r-gray-800"></div>
                        </div>
                      </div>
                    </div>
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Shared Claims
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Max Score
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-silver-200">
                {connections.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-4 py-8 text-center text-gray-500">
                      No network connections found for this entity
                    </td>
                  </tr>
                ) : (
                  connections.map((conn, index) => (
                    <tr key={index} className="table-row">
                      <td className="px-4 py-3 font-medium text-sm">
                        {conn.target_entity}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className="badge badge-blue">
                          {conn.connection_strength}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs text-gray-600">
                        {conn.shared_claim_numbers}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`font-bold text-sm ${
                          conn.max_shared_claim_fraud_score > 0.8 ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          {conn.max_shared_claim_fraud_score.toFixed(2)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`badge ${
                          conn.target_is_confirmed_fraud ? 'badge-red' : 'badge-gray'
                        }`}>
                          {conn.target_is_confirmed_fraud ? 'Fraud' : 'Unknown'}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }
  
  export default NetworkConnectionsTable;