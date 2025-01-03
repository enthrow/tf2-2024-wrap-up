import PlayerSummary from "./PlayerSummary";
import SharedSummary from "./SharedSummary";
import { NodeData } from "../types/nodeData";

interface SidePanelProps {
  type: "player" | "shared";
  nodeData?: NodeData;
  sharedData?: any[];
  loading: boolean;
  error: string | null;
  onClose: () => void;
}

const SidePanel: React.FC<SidePanelProps> = ({
  type,
  nodeData,
  sharedData,
  loading,
  error,
  onClose,
}) => {
    return (
        <div className="side-panel">
          <button className="close-button" onClick={onClose} aria-label="Close">
            &times;
          </button>
          <div className="panel-details">
            {loading && <p>Loading...</p>}
            {error && <p style={{ color: "red" }}>{error}</p>}
            {!loading && !error && type === "player" && nodeData && (
              <PlayerSummary nodeData={nodeData} />
            )}
            {!loading && !error && type === "shared" && sharedData && (
              <SharedSummary sharedData={sharedData} />
            )}
          </div>
        </div>
      );
    };
    
export default SidePanel;