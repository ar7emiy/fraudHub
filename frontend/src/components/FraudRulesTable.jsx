function FraudRulesTable({ rules }) {
    const getPriorityColor = (priority) => {
      switch(priority) {
        case 'High': return 'badge-red';
        case 'Medium': return 'badge-yellow';
        case 'Low': return 'badge-gray';
        default: return 'badge-gray';
      }
    };
  
    const getValueColor = (value) => {
      if (value >= 8) return 'text-red-600 font-bold';
      if (value >= 5) return 'text-orange-600';
      return 'text-gray-600';
    };
  
    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-navy-800 mb-3">Fraud Rules Triggered</h3>
        <div className="table-container">
          <div className="max-h-64 overflow-y-auto scrollable">
            <table className="w-full">
              <thead className="table-header">
                <tr>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Rule No.
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Rule Description
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Priority
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Value
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Claim Number(s)
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-silver-200">
                {rules.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-4 py-8 text-center text-gray-500">
                      No fraud rules triggered for this entity
                    </td>
                  </tr>
                ) : (
                  rules.map((rule, index) => (
                    <tr key={index} className="table-row">
                      <td className="px-4 py-3 text-center font-mono text-sm font-medium">
                        {rule.rule_no}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        {rule.rule_desc}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`badge ${getPriorityColor(rule.priority)}`}>
                          {rule.priority}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`font-bold text-sm ${getValueColor(rule.value)}`}>
                          {rule.value}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs text-gray-600 font-mono">
                        {rule.claim_numbers}
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
  
  export default FraudRulesTable;