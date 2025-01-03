import { useState, useEffect } from "react";
import { useRegisterEvents, useSigma } from "@react-sigma/core";
import { useNodeData } from "../hooks/useNodeData";
import SidePanel from "./SidePanel";

const NodeClickHandler: React.FC = () => {
  const sigma = useSigma();
  const graph = sigma.getGraph();
  const registerEvents = useRegisterEvents();

  // State to track the currently selected node
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // React Query hook to fetch node data
  const { data: nodeData, isLoading, error } = useNodeData(selectedNodeId ?? "");

  // Event registration for Sigma
  useEffect(() => {
    registerEvents({
      clickNode: ({ node }) => {
        // Reset highlight for all nodes
        console.log(`Node ID: ${node}`, graph.getNodeAttributes(node));
        graph.forEachNode((nodeId) => {
          graph.setNodeAttribute(nodeId, "highlighted", false);
        });

        // Highlight the clicked node
        graph.setNodeAttribute(node, "highlighted", true);

        // Set the selected node ID
        setSelectedNodeId(node);
      },
      clickStage: () => {
        // Deselect node and reset highlights when clicking on blank space
        setSelectedNodeId(null);
        graph.forEachNode((nodeId) => {
          graph.setNodeAttribute(nodeId, "highlighted", false);
        });
      },
    });
  }, [graph, registerEvents]);

  // Function to clear the selected node and close the side panel
  const clearNodeData = () => {
    setSelectedNodeId(null);
    graph.forEachNode((nodeId) => {
      graph.setNodeAttribute(nodeId, "highlighted", false);
    });
  };

  return (
    <>
      {selectedNodeId && (
        <SidePanel
          type="player"
          nodeData={nodeData}
          loading={isLoading}
          error={error?.message || null}
          onClose={clearNodeData}
        />
      )}
    </>
  );
};

export default NodeClickHandler;
