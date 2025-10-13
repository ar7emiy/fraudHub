function CommunityAnalysisTable({ communities, communityMembers }) {
  // Calculate fraud ratio for each community
  const getCommunityStats = () => {
    const stats = {};
    communityMembers.forEach(member => {
      if (!stats[member.community_id]) {
        stats[member.community_id] = { total: 0, fraud: 0 };
      }
      stats[member.community_id].total++;
      if (member.is_fraud) {
        stats[member.community_id].fraud++;
      }
    });
    return stats;
  };

  const communityStats = getCommunityStats();

  return (
    <div className="mb-6">
      <h3 className="text-lg font-semibold text-navy-800 mb-3">Algorithm-Derived Community Analysis</h3>
      <div className="grid grid-cols-2 gap-4">
        
        <div className="table-container">
          <div className="bg-gray-50 px-4 py-3 border-b border-silver-200">
            <h4 className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
              Community Members
            </h4>
            <p className="text-xs text-gray-500 mt-1">Other entities in this entity's communities</p>
          </div>
          <div className="max-h-48 overflow-y-auto scrollable">
            <table className="w-full">
              <thead className="table-header">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">
                    Community
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">
                    Member Name
                  </th>
                  <th className="px-4 py-2 text-center text-xs font-semibold text-gray-600 uppercase">
                    Fraud Flag
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-silver-200">
                {communityMembers.length === 0 ? (
                  <tr>
                    <td colSpan="3" className="px-4 py-8 text-center text-gray-500 text-sm">
                      No community memberships found
                    </td>
                  </tr>
                ) : (
                  communityMembers.map((member, index) => (
                    <tr key={index} className="table-row">
                      <td className="px-4 py-2 text-sm font-medium">
                        {member.community_id}
                      </td>
                      <td className="px-4 py-2 text-sm">
                        {member.entity_name}
                      </td>
                      <td className="px-4 py-2 text-center">
                        <span className={`badge ${
                          member.is_fraud ? 'badge-red' : 'badge-gray'
                        }`}>
                          {member.is_fraud ? 'FRAUD' : 'NORMAL'}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="table-container">
          <div className="bg-gray-50 px-4 py-3 border-b border-silver-200">
            <h4 className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
              Entity's Communities
            </h4>
            <p className="text-xs text-gray-500 mt-1">Communities this entity belongs to</p>
          </div>
          <div className="max-h-48 overflow-y-auto scrollable">
            <table className="w-full">
              <thead className="table-header">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">
                    Community ID
                  </th>
                  <th className="px-4 py-2 text-center text-xs font-semibold text-gray-600 uppercase">
                    Fraud Ratio
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-silver-200">
                {communities.length === 0 ? (
                  <tr>
                    <td colSpan="2" className="px-4 py-8 text-center text-gray-500 text-sm">
                      Entity not in any communities
                    </td>
                  </tr>
                ) : (
                  communities.map((community, index) => {
                    const stats = communityStats[community.community_id];
                    const fraudRatio = stats ? (stats.fraud / stats.total) : 0;
                    const getRiskColor = (ratio) => {
                      if (ratio > 0.6) return 'badge-red';
                      if (ratio > 0.3) return 'badge-yellow';
                      return 'badge-green';
                    };
                    
                    return (
                      <tr key={index} className="table-row">
                        <td className="px-4 py-2 text-sm font-medium">
                          Community {community.community_id}
                        </td>
                        <td className="px-4 py-2 text-center">
                          <span className={`badge ${getRiskColor(fraudRatio)}`}>
                            {(fraudRatio * 100).toFixed(0)}% ({stats ? stats.fraud : 0}/{stats ? stats.total : 0})
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CommunityAnalysisTable;