# Analysing how an algorithm handles scaling grpahs at a fixed density
import time
from numpy import std

from database.db_manager import MongoDBManager
from utils.generate_graph import generate_graph_nd
from analysis.measurements import measure_runtime, measure_memory
from utils.get_graph import get_graphs_nd

def analyse_algorithm_scalability(algorithm, density, node_sizes, num_graphs=10, db_manager = None):
    """
    Evaluate the scalability of a given graph algorithm by testing its performance across 
    different graph sizes at a fixed density.

    Parameters:
    ----------
    algorithm : callable
        The graph algorithm to be evaluated. Should accept a graph as input and return 
        relevant output or results.
    
    density: float
         Density represents the ratio of 
        actual edges to possible edges in a graph (e.g., 0.1 means 10% of all possible edges).
    
    node_sizes : list of int
        A list of node counts (e.g., [100, 200, 500, 1000, 2000, 5000, 10000]) representing 
        different graph sizes for evaluating algorithm scalability.
    
    num_graphs : int, optional, default=10
        The number of random graphs to generate for each combination of node count and 
        density, ensuring statistical significance in performance metrics.

    Procedure:
    ---------

    3. **Determine Graph Sizes**:
       - The `node_sizes` parameter defines various graph sizes (number of nodes) to evaluate 
         the algorithm’s performance as the graph scales.

    4. **Generate Random Graphs**:
       - For each combination of node count (N) and density (D), generate `num_graphs` random graphs 
         to ensure consistency and statistical significance in performance metrics.

    5. **Run the Algorithm and Collect Data**:
       - For each generated graph:
         a. Execute the algorithm.
         b. Measure execution time using a high-resolution timer.
         c. Track peak memory usage during execution.
       - Record the performance metrics for later analysis.

    """
    if not db_manager:
        db_manager = MongoDBManager()
    # Run for each
    results = {}

    for node_size in node_sizes:
        graphs = []

        graphs = get_graphs_nd("random", node_size, density, num_graphs, db_manager)

        runtimes = []
        memories = []
        for graph in graphs:
            _, runtime = measure_runtime(algorithm, graph)
            runtimes.append(runtime)

            _, peak_memory = measure_memory(algorithm, graph)
            memories.append(peak_memory)

        avg_runtime = sum(runtimes)/ len(runtimes)
        std_runtime = std(runtimes)
        min_runtime = min(runtimes)
        max_runtime = max(runtimes)
        avg_memory = sum(memories)/ len(memories)
        std_memory = std(memories)
        min_memory = min(memories)
        max_memory = max(memories)

        results.update({node_size: {
            "avg_runtime": avg_runtime,
            "std_runtime": std_runtime,
            "min_runtime": min_runtime,
            "max_runtime": max_runtime,
            "avg_memory": avg_memory,
            "std_memory": std_memory,
            "min_memory": min_memory,
            "max_memory": max_memory
        }})
    return results


if __name__ == "__main__":
    density = 0.1
    node_sizes = [15]
    num_graphs = 3

    analyse_algorithm_scalability(None, density, node_sizes)
            





