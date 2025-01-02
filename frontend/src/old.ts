import Graph from "graphology";
import { parse } from "graphology-gexf/browser";
import Sigma from "sigma";

// Initialize the graph rendering and controls
let renderer: Sigma | null = null;

// Fetch and parse the GEXF graph
fetch("/kyle.gexf")
  .then((res) => res.text())
  .then((gexf) => {
    const graph = parse(Graph, gexf);

    // Hide all edges in the graph
    graph.forEachEdge((edgeId) => {
      graph.setEdgeAttribute(edgeId, "hidden", true);
    });

    // Retrieve DOM elements
    const container = document.getElementById("sigma-container") as HTMLElement;
    const zoomInBtn = document.getElementById("zoom-in") as HTMLButtonElement;
    const zoomOutBtn = document.getElementById("zoom-out") as HTMLButtonElement;
    const zoomResetBtn = document.getElementById("zoom-reset") as HTMLButtonElement;
    const labelsThresholdRange = document.getElementById("labels-threshold") as HTMLInputElement;
    

    // Initialize Sigma
    renderer = new Sigma(graph, container, {
      // minCameraRatio: 0.08,
      // maxCameraRatio: 3,
    });

    // Dynamically set scalingRatio
    renderer.setSetting("autoRescale", false); // Increase node and edge sizes
    renderer.setSetting("zoomToSizeRatioFunction", (ratio) => ratio)

    const camera = renderer.getCamera();

    camera.setState({
      x: 0,       // Center x-coordinate
      y: 0,       // Center y-coordinate
      ratio: 40, // Initial zoom level (lower means more zoomed in)
    });

    // Bind zoom controls
    zoomInBtn.addEventListener("click", () => {
      camera.animatedZoom({ duration: 600 });
    });

    zoomOutBtn.addEventListener("click", () => {
      camera.animatedUnzoom({ duration: 600 });
    });

    zoomResetBtn.addEventListener("click", () => {
      camera.animatedReset({ duration: 600 });
    });

    // Bind label threshold slider
    labelsThresholdRange.addEventListener("input", () => {
      renderer?.setSetting("labelRenderedSizeThreshold", +labelsThresholdRange.value);
    });

    // Set initial slider value
    labelsThresholdRange.value = renderer.getSetting("labelRenderedSizeThreshold") + "";
  });

// Clean up renderer if needed
window.addEventListener("beforeunload", () => {
  renderer?.kill();
});
