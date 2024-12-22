import React, { useState, useEffect, useRef } from 'react';
import ForceGraph3D from 'react-force-graph-3d';

const App = () => {
  const [graphData, setGraphData] = useState(null);
  const [selectedFile, setSelectedFile] = useState('test1.json'); // Default file
  const [searchValue, setSearchValue] = useState(''); // For the search input
  const graphRef = useRef(); // Reference to the graph component

  // List of available JSON files
  const files = [
    { label: 'File 1', value: 'test1.json' },
    { label: 'File 2', value: 'test2.json' },
    { label: 'File 3', value: 'test3.json' },
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

  const handleSearch = () => {
    if (!graphData || !searchValue) return;
  
    // Find the node by ID or name
    const node = graphData.nodes.find(
      (n) => n.id.toString() === searchValue || n.id?.toString() === searchValue
    );
  
    if (node) {
      // Calculate a closer zoom position
      const distanceFactor = 1.02; // Adjust this to control zoom distance (higher = farther)
      const closerPosition = {
        x: node.x / distanceFactor,
        y: node.y / distanceFactor,
        z: node.z / distanceFactor,
      };
  
      // Zoom to the node
      graphRef.current.cameraPosition(
        closerPosition, // Position slightly farther than the node
        node, // Look-at the node
        3000 // Animation duration in ms
      );
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
          graphData={graphData}
          enableNodeDrag={false} // Disable dragging
          forceEngine="d3" // Use d3 for predictable behavior
          d3AlphaDecay={0} // Stop internal force decay
          d3VelocityDecay={0} // Stop velocity decay
          cooldownTicks={0} // Completely stop the layout simulation
          nodeLabel={(node) => `${node.id}: ${node.val}`}
          nodeVal={(node) => node.val}
          // linkWidth={(link) => link.val / 2}
          nodeAutoColorBy="val"        
        />
      </div>
  );
};

export default App;
