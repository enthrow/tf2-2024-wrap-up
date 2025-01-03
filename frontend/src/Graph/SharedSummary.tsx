import React from "react";

interface SharedSummaryProps {
  sharedData: any[];
}

const SharedSummary: React.FC<SharedSummaryProps> = ({ sharedData }) => {
  const [node1, node2] = sharedData;

  return (
    <div>
      <h2>Shared Summary</h2>
      <p><strong>Node 1:</strong> {node1}</p>
      <p><strong>Node 2:</strong> {node2}</p>
      <h3>Shared Attributes (Example)</h3>
      <ul>
        <li>Shared Attribute 1: Value</li>
        <li>Shared Attribute 2: Value</li>
        {/* Replace with actual shared attribute comparisons */}
      </ul>
    </div>
  );
};

export default SharedSummary;
