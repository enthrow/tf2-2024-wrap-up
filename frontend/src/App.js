import React, { useState, useEffect, useRef, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';

const App = () => {
  const [graphData, setGraphData] = useState(null);
  const [selectedFile, setSelectedFile] = useState('3_pages.json'); // Default file
  const [searchValue, setSearchValue] = useState(''); // For the search input
  const graphRef = useRef(); // Reference to the graph component

  // List of available JSON files
  const files = [
    { label: '3_pages', value: '3_pages.json' },
    { label: '100_pages', value: '100_pages.json' },
    { label: 'all_logs', value: 'all_logs.json' },
  ];

  // Load the selected JSON file
  useEffect(() => {
    fetch(`/graphs/${selectedFile}`)
      .then((response) => response.json())
      .then((data) => setGraphData(data))
      .catch((error) => console.error('Error loading data:', error));
  }, [selectedFile]);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.value); // Update the selected file
  };

  // Unified focus function
  const focusNode = useCallback((node) => {
    if (!node) return;

    const distance = 300; // Adjust distance as needed
    const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);

    graphRef.current.cameraPosition(
      { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // New camera position
      node, // Look-at the node
      3000 // Animation duration (ms)
    );
  }, []);

  const handleNodeClick = useCallback(
    (node) => {
      focusNode(node); // Focus on the clicked node
    },
    [focusNode]
  );

  const handleSearch = () => {
    if (!graphData || !searchValue) return;

    // Find the node by ID or name
    const node = graphData.nodes.find(
      (n) => n.id.toString() === searchValue || n.name?.toString() === searchValue
    );

    if (node) {
      focusNode(node); // Use the same focus logic for the search
    } else {
      alert('Node not found');
    }
  };

  if (!graphData) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      {/* Dropdown Menu */}
      <div style={{ position: 'absolute', top: 10, left: 10, zIndex: 1000 }}>
        <label htmlFor="file-selector">Select a File: </label>
        <select
          id="file-selector"
          value={selectedFile}
          onChange={handleFileChange}
          style={{ padding: '5px', fontSize: '16px' }}
        >
          {files.map((file) => (
            <option key={file.value} value={file.value}>
              {file.label}
            </option>
          ))}
        </select>
      </div>

      {/* Search Bar */}
      <div style={{ position: 'absolute', top: 50, left: 10, zIndex: 1000 }}>
        <input
          type="text"
          placeholder="Search for a node"
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          style={{ padding: '5px', fontSize: '16px', marginRight: '10px' }}
        />
        <button onClick={handleSearch} style={{ padding: '5px', fontSize: '16px' }}>
          Search
        </button>
      </div>

      {/* Force Graph */}
      <ForceGraph3D
        ref={graphRef}
        graphData={graphData}
        enableNodeDrag={false} // Disable dragging
        forceEngine="d3" // Use d3 for predictable behavior
        d3AlphaDecay={0} // Stop internal force decay
        d3VelocityDecay={0} // Stop velocity decay
        cooldownTicks={0} // Completely stop the layout simulation
        nodeLabel={(node) => `${node.id}: ${node.val}`}
        nodeVal={(node) => node.val}
        nodeAutoColorBy="val"
        linkVisibility={false} // Do not render links
        onNodeClick={handleNodeClick} // Attach click-to-focus
      />
    </div>
  );
};

export default App;
