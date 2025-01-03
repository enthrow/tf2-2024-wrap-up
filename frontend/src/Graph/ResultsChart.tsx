import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

interface ResultsChartProps {
  results: {
    won: number;
    lost: number;
    tied: number;
  };
}

const COLORS = {
    wins: "#28a745", // Green for wins
    losses: "#dc3545", // Red for losses
    ties: "#007bff", // Blue for ties
  };
const ResultsChart: React.FC<ResultsChartProps> = ({ results }) => {
  const pieData = [
    { name: "Wins", value: results.won },
    { name: "Losses", value: results.lost },
    { name: "Ties", value: results.tied },
  ];

  return (
    <PieChart width={300} height={300}>
      <Pie
        data={pieData}
        dataKey="value"
        nameKey="name"
        cx="50%"
        cy="50%"
        outerRadius={100}
        innerRadius={50}
        fill="#8884d8"
        label
      >
        {pieData.map((entry, index) => (
          <Cell
            key={`cell-${index}`}
            fill={COLORS[entry.name.toLowerCase() as keyof typeof COLORS]}
          />
        ))}
      </Pie>
      <Tooltip />
      <Legend />
    </PieChart>
  );
};

export default ResultsChart;
