function ClaimsTable({ claims }) {
    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-navy-800 mb-3">Associated Claims</h3>
        <div className="table-container">
          <div className="max-h-64 overflow-y-auto scrollable">
            <table className="w-full">
              <thead className="table-header">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Claim Number
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    External Score
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Incurred
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Other Entities
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-silver-200">
                {claims.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="px-4 py-8 text-center text-gray-500">
                      No claims found for this entity
                    </td>
                  </tr>
                ) : (
                  claims.map((claim, index) => (
                    <tr key={index} className="table-row">
                      <td className="px-4 py-3 font-mono text-sm font-medium">
                        {claim.claim_number}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`font-bold text-sm ${
                          claim.external_fraud_score > 0.8 ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          {claim.external_fraud_score.toFixed(2)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center font-medium">
                        ${claim.total_incurred.toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-xs text-gray-600">
                        {claim.other_entities_on_claim}
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
  
  export default ClaimsTable;