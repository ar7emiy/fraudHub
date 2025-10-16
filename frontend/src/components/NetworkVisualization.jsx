import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Network, Maximize2, RefreshCw } from 'lucide-react';

const NetworkVisualization = ({
  selectedEntity,
  onNodeSelect,
  onNodeDoubleClick,
  sortBy = 'ensemble_score'
}) => {
  const [networkData, setNetworkData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('ego'); // 'full', 'community', 'ego'
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());
  const [hoverNode, setHoverNode] = useState(null);

  const fgRef = useRef();
  const containerRef = useRef();

  // Community color palette (vibrant colors for visual distinction)
  const communityColors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788'
  ];

  // Load network data
  useEffect(() => {
    const loadNetworkData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5000/api/network-data');
        const result = await response.json();

        console.log('Network data loaded:', result);

        if (result.success) {
          console.log('Nodes:', result.data.nodes.length, 'Edges:', result.data.edges.length);
          setNetworkData(result.data);
        } else {
          setError('Failed to load network data');
        }
      } catch (err) {
        setError('Error connecting to server');
        console.error('Error loading network data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadNetworkData();
  }, []);

  // Filter data based on view mode
  const filteredData = useMemo(() => {
    if (!networkData || !selectedEntity) {
      console.log('Returning full networkData:', networkData?.nodes?.length, 'nodes');
      return networkData;
    }

    const selectedNodeId = selectedEntity.entity_name;
    console.log('Filtering for entity:', selectedNodeId, 'in mode:', viewMode);

    if (viewMode === 'full') {
      // Show all nodes, but highlight ego network
      return networkData;
    }

    if (viewMode === 'ego') {
      // Show only selected entity and its direct neighbors
      const connectedNodeIds = new Set([selectedNodeId]);

      networkData.edges.forEach(edge => {
        if (edge.source === selectedNodeId || edge.source.id === selectedNodeId) {
          const targetId = edge.target.id || edge.target;
          connectedNodeIds.add(targetId);
        }
        if (edge.target === selectedNodeId || edge.target.id === selectedNodeId) {
          const sourceId = edge.source.id || edge.source;
          connectedNodeIds.add(sourceId);
        }
      });

      const filteredNodes = networkData.nodes.filter(node =>
        connectedNodeIds.has(node.id)
      );

      const filteredEdges = networkData.edges.filter(edge => {
        const sourceId = edge.source.id || edge.source;
        const targetId = edge.target.id || edge.target;
        return connectedNodeIds.has(sourceId) && connectedNodeIds.has(targetId);
      });

      return {
        ...networkData,
        nodes: filteredNodes,
        edges: filteredEdges
      };
    }

    if (viewMode === 'community') {
      // Show only entities in the same communities as selected entity
      const selectedNode = networkData.nodes.find(n => n.id === selectedNodeId);
      if (!selectedNode || !selectedNode.communities || selectedNode.communities.length === 0) {
        return { nodes: [selectedNode || networkData.nodes[0]], edges: [] };
      }

      const selectedCommunities = new Set(selectedNode.communities);
      const communityNodeIds = new Set();

      networkData.nodes.forEach(node => {
        if (node.communities && node.communities.some(c => selectedCommunities.has(c))) {
          communityNodeIds.add(node.id);
        }
      });

      const filteredNodes = networkData.nodes.filter(node =>
        communityNodeIds.has(node.id)
      );

      const filteredEdges = networkData.edges.filter(edge => {
        const sourceId = edge.source.id || edge.source;
        const targetId = edge.target.id || edge.target;
        return communityNodeIds.has(sourceId) && communityNodeIds.has(targetId);
      });

      return {
        ...networkData,
        nodes: filteredNodes,
        edges: filteredEdges
      };
    }

    return networkData;
  }, [networkData, selectedEntity, viewMode]);

  // Update highlight when selected entity changes
  useEffect(() => {
    if (!filteredData || !selectedEntity) return;

    const selectedNodeId = selectedEntity.entity_name;
    const highlightNodesSet = new Set([selectedNodeId]);
    const highlightLinksSet = new Set();

    if (filteredData.edges) {
      filteredData.edges.forEach(edge => {
        const sourceId = edge.source.id || edge.source;
        const targetId = edge.target.id || edge.target;

        if (sourceId === selectedNodeId || targetId === selectedNodeId) {
          highlightLinksSet.add(edge);
          highlightNodesSet.add(sourceId);
          highlightNodesSet.add(targetId);
        }
      });
    }

    setHighlightNodes(highlightNodesSet);
    setHighlightLinks(highlightLinksSet);

    // Center on selected node
    if (fgRef.current && selectedEntity) {
      const node = filteredData.nodes.find(n => n.id === selectedNodeId);
      if (node) {
        fgRef.current.centerAt(node.x, node.y, 1000);
        fgRef.current.zoom(3, 1000);
      }
    }
  }, [selectedEntity, filteredData]);

  // Get node color based on community (with gradient for multi-community)
  const getNodeColor = useCallback((node) => {
    // Check if confirmed fraud or "Bad Actor" status
    const isBadActor = node.investigationStatus === 'Bad Actor';
    const isFraud = node.isFraud === 1;

    if (!node.communities || node.communities.length === 0) {
      return '#95A5A6'; // Gray for no community
    }

    if (node.communities.length === 1) {
      return communityColors[node.communities[0] % communityColors.length];
    }

    // Multi-community: return primary community color (we'll handle gradient in paint)
    return communityColors[node.communities[0] % communityColors.length];
  }, []);

  // Get node size based on sortBy filter
  const getNodeSize = useCallback((node) => {
    const baseSize = 3;
    const maxSize = 12;
    const minSize = 3;

    if (!filteredData) return baseSize;

    // Determine which metric to use
    const metric = sortBy === 'total_exposure' ? 'financialExposure' : 'riskScore';
    const values = filteredData.nodes.map(n => n[metric]);
    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);

    if (maxValue === minValue) return baseSize;

    const normalized = (node[metric] - minValue) / (maxValue - minValue);
    const size = minSize + (normalized * (maxSize - minSize));

    // Selected node is slightly larger
    if (selectedEntity && node.id === selectedEntity.entity_name) {
      return size * 1.3;
    }

    return size;
  }, [filteredData, sortBy, selectedEntity]);

  // Custom node painting
  const paintNode = useCallback((node, ctx, globalScale) => {
    // Safety check: ensure node has coordinates
    if (!node.x || !node.y || !isFinite(node.x) || !isFinite(node.y)) {
      return;
    }

    const size = getNodeSize(node);
    const isSelected = selectedEntity && node.id === selectedEntity.entity_name;
    const isHighlighted = highlightNodes.has(node.id);
    const isHovered = hoverNode && hoverNode.id === node.id;
    const isFraud = node.isFraud === 1 || node.investigationStatus === 'Bad Actor';

    // Dimming for non-highlighted nodes in full view
    const baseOpacity = (viewMode === 'full' && selectedEntity && !isHighlighted) ? 0.3 : 1;

    // Draw node
    if (node.communities && node.communities.length > 1) {
      // Multi-community: gradient
      const gradient = ctx.createLinearGradient(
        node.x - size, node.y - size,
        node.x + size, node.y + size
      );
      node.communities.slice(0, 3).forEach((commId, idx) => {
        const color = communityColors[commId % communityColors.length];
        gradient.addColorStop(idx / Math.min(node.communities.length, 3), color);
      });
      ctx.fillStyle = gradient;
    } else {
      ctx.fillStyle = getNodeColor(node);
    }

    ctx.globalAlpha = baseOpacity;
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.fill();

    // Fraud entity border (thick dark red)
    if (isFraud) {
      ctx.strokeStyle = '#8B0000';
      ctx.lineWidth = 2 / globalScale;
      ctx.globalAlpha = 1;
      ctx.stroke();
    }

    // Selection ring
    if (isSelected) {
      ctx.strokeStyle = '#2C3E50';
      ctx.lineWidth = 3 / globalScale;
      ctx.globalAlpha = 1;
      ctx.beginPath();
      ctx.arc(node.x, node.y, size + 2, 0, 2 * Math.PI);
      ctx.stroke();
    }

    // Hover glow
    if (isHovered) {
      ctx.strokeStyle = '#F39C12';
      ctx.lineWidth = 2 / globalScale;
      ctx.globalAlpha = 0.6;
      ctx.beginPath();
      ctx.arc(node.x, node.y, size + 1, 0, 2 * Math.PI);
      ctx.stroke();
    }

    // Draw label for selected or hovered nodes
    if ((isSelected || isHovered) && globalScale > 1) {
      ctx.globalAlpha = 1;
      ctx.font = `${12 / globalScale}px Sans-Serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#2C3E50';
      ctx.fillText(node.name, node.x, node.y + size + 8 / globalScale);
    }

    ctx.globalAlpha = 1;
  }, [getNodeSize, getNodeColor, selectedEntity, highlightNodes, hoverNode, viewMode]);

  // Custom link painting
  const paintLink = useCallback((link, ctx, globalScale) => {
    // Safety check: ensure link endpoints have coordinates
    if (!link.source || !link.target ||
        !isFinite(link.source.x) || !isFinite(link.source.y) ||
        !isFinite(link.target.x) || !isFinite(link.target.y)) {
      return;
    }

    const isHighlighted = highlightLinks.has(link);
    const baseOpacity = (viewMode === 'full' && selectedEntity && !isHighlighted) ? 0.15 : 0.4;

    // Edge thickness based on weight
    const maxWeight = filteredData ? Math.max(...filteredData.edges.map(e => e.weight)) : 1;
    const thickness = (link.weight / maxWeight) * 3 + 0.5;

    // Edge color based on connection strength (milder hue)
    const strength = link.weight / maxWeight;
    const colorIntensity = Math.floor(150 + strength * 105); // Range from 150-255
    const color = `rgb(${colorIntensity}, ${colorIntensity}, ${colorIntensity})`;

    ctx.strokeStyle = color;
    ctx.lineWidth = thickness / globalScale;
    ctx.globalAlpha = isHighlighted ? 0.8 : baseOpacity;

    ctx.beginPath();
    ctx.moveTo(link.source.x, link.source.y);
    ctx.lineTo(link.target.x, link.target.y);
    ctx.stroke();

    ctx.globalAlpha = 1;
  }, [highlightLinks, filteredData, viewMode, selectedEntity]);

  // Handle node click
  const handleNodeClick = useCallback((node) => {
    onNodeSelect(node);
  }, [onNodeSelect]);

  // Handle node double-click
  const handleNodeDoubleClick = useCallback((node) => {
    onNodeDoubleClick(node);
  }, [onNodeDoubleClick]);

  // Handle node hover
  const handleNodeHover = useCallback((node) => {
    setHoverNode(node);
    if (containerRef.current) {
      containerRef.current.style.cursor = node ? 'pointer' : 'default';
    }
  }, []);

  // Handle link hover (show tooltip)
  const handleLinkHover = useCallback((link) => {
    // Could implement tooltip here
  }, []);

  // Reset layout
  const handleResetLayout = useCallback(() => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(400);
    }
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-lightblue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading network...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50">
        <div className="text-center text-red-600">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!filteredData || !filteredData.nodes || filteredData.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900">
        <div className="text-center text-white">
          <p>No network data available</p>
          <p className="text-sm text-gray-400 mt-2">Select an entity to view their network</p>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="relative w-full h-full bg-gray-900">
      {/* Floating control panel */}
      <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-3 z-10 space-y-2">
        <div className="flex items-center gap-2 mb-2">
          <Network size={18} className="text-navy-800" />
          <span className="font-semibold text-sm text-navy-800">Network View</span>
        </div>

        <div className="space-y-1">
          <label className="text-xs text-gray-600 block">View Mode</label>
          <select
            value={viewMode}
            onChange={(e) => setViewMode(e.target.value)}
            className="w-full text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-lightblue-500"
          >
            <option value="ego">Ego Network</option>
            <option value="community">Community View</option>
            <option value="full">Full Network</option>
          </select>
        </div>

        <button
          onClick={handleResetLayout}
          className="w-full flex items-center justify-center gap-2 bg-lightblue-500 hover:bg-lightblue-600 text-white text-sm px-3 py-1.5 rounded transition-colors"
        >
          <RefreshCw size={14} />
          Reset Layout
        </button>

        {/* Legend */}
        <div className="border-t border-gray-200 pt-2 mt-2">
          <p className="text-xs font-semibold text-gray-700 mb-1">Legend</p>
          <div className="space-y-1 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full border-2 border-red-900"></div>
              <span className="text-gray-600">Fraud Entity</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gradient-to-r from-red-400 to-blue-400"></div>
              <span className="text-gray-600">Multi-Community</span>
            </div>
            <div className="flex items-center gap-2">
              <Maximize2 size={12} className="text-gray-600" />
              <span className="text-gray-600">Size: {sortBy === 'total_exposure' ? 'Financial' : 'Risk Score'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Force Graph */}
      <ForceGraph2D
        ref={fgRef}
        graphData={{
          nodes: filteredData.nodes,
          links: filteredData.edges
        }}
        nodeId="id"
        nodeLabel={node => `${node.name}\nRisk: ${node.riskScore.toFixed(1)}\nExposure: $${node.financialExposure.toLocaleString()}`}
        nodeCanvasObject={paintNode}
        nodeCanvasObjectMode={() => 'replace'}
        linkCanvasObject={paintLink}
        linkCanvasObjectMode={() => 'replace'}
        linkLabel={link => `Shared Claims: ${link.claimNumbers}\nConnection Strength: ${link.weight}`}
        onNodeClick={handleNodeClick}
        onNodeRightClick={handleNodeDoubleClick}
        onNodeHover={handleNodeHover}
        onLinkHover={handleLinkHover}
        enableNodeDrag={true}
        enableZoomInteraction={true}
        enablePanInteraction={true}
        cooldownTime={3000}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
        warmupTicks={100}
        cooldownTicks={0}
      />

      {/* Instructions overlay */}
      {selectedEntity && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-white/90 rounded-lg shadow-lg px-4 py-2 text-sm text-gray-700">
          Click node to select • Right-click to view details
        </div>
      )}
    </div>
  );
};

export default NetworkVisualization;
