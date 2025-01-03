import React, { useState } from "react";
import { NodeData } from "../types/nodeData";
import ResultsChart from "./ResultsChart"
import DropdownMenu from "./DropdownMenu";
// import { ResponsiveContainer } from "recharts";

interface PlayerSummaryProps {
  nodeData: NodeData;
}

const PlayerSummary: React.FC<PlayerSummaryProps> = ({ nodeData }) => {
  const [activeTab, setActiveTab] = useState<"games" | "maps" | "formats">("games");

  return (
    <div className="player-summary">
      <div style={{ display: "flex", alignItems: "center", marginBottom: "1em" }}>
              <h1>
                {nodeData.name}
              </h1>
              <DropdownMenu id={nodeData.id} />
            </div>
      <div className="tabs">
        <button
          className={activeTab === "games" ? "active-tab" : ""}
          onClick={() => setActiveTab("games")}
        >
          Games
        </button>
        <button
          className={activeTab === "maps" ? "active-tab" : ""}
          onClick={() => setActiveTab("maps")}
        >
          Maps
        </button>
        <button
          className={activeTab === "formats" ? "active-tab" : ""}
          onClick={() => setActiveTab("formats")}
        >
          Formats
        </button>
      </div>
      <div className="tab-content">
        {activeTab === "games" && (
          <>
            <p><strong>Total Games:</strong> {nodeData.total_games}</p> {/* Add total_games here */}
            <ResultsChart results={nodeData.results} />
          </>
        )}
        {activeTab === "maps" && (
          <ul>
            {Object.entries(nodeData.maps).map(([map, count]) => (
              <li key={map}>
                <strong>{map}:</strong> {count}
              </li>
            ))}
          </ul>
        )}
        {activeTab === "formats" && (
          <ul>
            {Object.entries(nodeData.formats).map(([format, count]) => (
              <li key={format}>
                <strong>{format}:</strong> {count}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default PlayerSummary;
