import "@react-sigma/core/lib/react-sigma.min.css";
import { SigmaContainer, ControlsContainer, ZoomControl, SearchControl, FullScreenControl } from "@react-sigma/core";
import LoadGraph from "./LoadGraph";
import NodeClickHandler from "./NodeClickHandler";

function DisplayGraph() {
  return (
    <SigmaContainer
      settings={{
        autoRescale: true,
        itemSizesReference: "positions",
        labelRenderedSizeThreshold: 10,
        labelColor: {color: "#ffffff"},
        zoomToSizeRatioFunction: (ratio) => ratio,
      }}
      style={{ width: "100vw", height: "100vh" }}
    >
      <LoadGraph />
      <NodeClickHandler />
      {/* Add Zoom Buttons */}
      <ControlsContainer position="top-right">
        <SearchControl />
      </ControlsContainer>
      <ControlsContainer position="top-left">
        <ZoomControl />
        <FullScreenControl />
      </ControlsContainer>
    </SigmaContainer>
  );
}

export default DisplayGraph;
