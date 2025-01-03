import { useEffect } from "react";
import { useLoadGraph } from "@react-sigma/core";
import { parse } from "graphology-gexf";
import Graph from "graphology";

function LoadGraph() {
  const loadGraph = useLoadGraph();
  useEffect(() => {
    const fetchAndLoadGraph = async () => {
      try {
        // Fetch the GEXF file
        const response = await fetch("/noedges.gexf");
        if (!response.ok) {
          throw new Error("Failed to fetch the GEXF file.");
        }
        
        // Parse the GEXF content
        const text = await response.text();
        const graph = parse(Graph, text);

        // don't render edges. We should never have edges in our data anyways as hiding them doesn't help load times.
        graph.forEachEdge((edgeId) => {
            graph.setEdgeAttribute(edgeId, "hidden", true);
          });
                
        // Load the parsed graph into Sigma
        loadGraph(graph);
      } catch (err) {
        console.error("Error loading the GEXF file:", err);
      }
    };

    fetchAndLoadGraph();
  }, [loadGraph]);

  return null;
}

export default LoadGraph;