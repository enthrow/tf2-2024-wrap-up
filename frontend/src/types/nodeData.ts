export interface NodeData {
    id: string;
    name: string;
    total_games: number;
    results: {
      won: number;
      lost: number;
      tied: number;
    };
    formats: Record<string, number>;
    maps: Record<string, number>;
  }
  
  export interface SidePanelProps {
    nodeData: NodeData;
    loading: boolean;
    error: string | null;
    onClose: () => void;
  }
  