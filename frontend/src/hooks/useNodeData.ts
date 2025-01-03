import { useQuery } from "@tanstack/react-query";

// Fetch function
const fetchNodeData = async (id: string): Promise<any> => {
  const response = await fetch(`http://127.0.0.1:5000/players/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch node data for ID: ${id}`);
  }
  return response.json();
};

// Custom hook
export const useNodeData = (id: string) => {
  return useQuery({
    queryKey: ["nodeData", id], // Unique query key
    queryFn: () => fetchNodeData(id), // Fetch function
    enabled: !!id, // Only run the query if `id` is provided
    staleTime: 60000, // Data is considered fresh for 1 minute
    gcTime: 300000, // Data remains in cache for 5 minutes
    retry: 2, // Retry failed requests up to 2 times
    refetchOnWindowFocus: false, // Disable refetching when the window regains focus
  });
};
