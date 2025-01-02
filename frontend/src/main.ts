import Graph from "graphology";
import { parse } from "graphology-gexf/browser";
import Sigma from "sigma";

// Initialize the graph rendering and controls
let renderer: Sigma | null = null;

// get and parse graph from gexf file
fetch("/bad.gexf")
  .then((res) => res.text())
  .then((gexf) => {
    const graph = parse(Graph, gexf);

    // hide all edges in the graph we have too many; it will melt your computer.
    graph.forEachEdge((edgeId) => {
      graph.setEdgeAttribute(edgeId, "hidden", true);
    });
    // get DOM elements
    const container = document.getElementById("sigma-container") as HTMLElement;
    const zoomInBtn = document.getElementById("zoom-in") as HTMLButtonElement;
    const zoomOutBtn = document.getElementById("zoom-out") as HTMLButtonElement;
    const zoomResetBtn = document.getElementById("zoom-reset") as HTMLButtonElement;
    const summaryBox = document.getElementById("summary-box") as HTMLElement;
    const summaryCloseBtn = document.getElementById("summary-close") as HTMLElement;
    const summaryContent = document.getElementById("summary-content") as HTMLElement;

    // become sigma
    renderer = new Sigma(graph, container, {
      minCameraRatio: 0.01,
      maxCameraRatio: 40,
      autoRescale: false,
      zoomToSizeRatioFunction: ((ratio) => ratio),
      labelRenderedSizeThreshold: 30,
    });    

    // camera settings
    const initialCameraState = {
      x: 0,
      y: 0,
      ratio: 50, // more = further out, do this automagically
      angle: 0.2, // makes labels look better
    };
    const camera = renderer.getCamera();
    camera.setState(initialCameraState);


    // bind controls for buttons
    zoomInBtn.addEventListener("click", () => {
      camera.animatedZoom({ duration: 300 });
    });

    zoomOutBtn.addEventListener("click", () => {
      camera.animatedUnzoom({ duration: 300 });
    });

    zoomResetBtn.addEventListener("click", () => {
      camera.animate(initialCameraState, { duration: 300 });
    });

    // Add node click event listener
    renderer.on("clickNode", (event) => {
      const nodeId = event.node;

      // Fetch additional node details from API
      fetch(`http://127.0.0.1:5000/players/${nodeId}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          summaryContent.innerHTML = `
            <h3>Error</h3>
            <p>${data.error}</p>
          `;
          summaryBox.style.display = "block";
          return;
        }
  
        // Build the HTML for the summary box
        summaryContent.innerHTML = `
          <h3>Node Summary</h3>
          <p><strong>ID:</strong> ${data.id}</p>
          <p><strong>Name:</strong> ${data.name}</p>
          <h4>Games</h4>
          <ul>
            <li><strong>Total:</strong> ${data.games.total}</li>
            <li><strong>Won:</strong> ${data.games.won}</li>
            <li><strong>Lost:</strong> ${data.games.lost}</li>
            <li><strong>Tied:</strong> ${data.games.tied}</li>
          </ul>
          <h4>Maps</h4>
          <ul>
            ${Object.entries(data.maps).map(
              ([map, count]) => `<li><strong>${map}:</strong> ${count}</li>`
            ).join("")}
          </ul>
          <h4>Formats</h4>
          <ul>
            ${Object.entries(data.formats).map(
              ([format, count]) => `<li><strong>${format}:</strong> ${count}</li>`
            ).join("")}
          </ul>
        `;


        summaryBox.style.display = "block";
        });
    });

    // Add event listener to close the summary box
    summaryCloseBtn.addEventListener("click", () => {
      summaryBox.style.display = "none";
    });

    // Hide summary when clicking on blank graph space
    renderer.on("clickStage", () => {
      summaryBox.style.display = "none";
    });
  });
// clean up renderer if needed
window.addEventListener("beforeunload", () => {
  renderer?.kill();
});
