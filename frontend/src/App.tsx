import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import DisplayGraph from "./Graph/DisplayGraph"; // Your main app component
import "./app.css"

const queryClient = new QueryClient();

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <DisplayGraph />
    </QueryClientProvider>
  );
};

export default App;
