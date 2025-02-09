import statistics
from analysis.measurements import measure_runtime, measure_memory
from utils.validation import valid_algorithms

def run_coloring_experiment(graphs, algorithm_names, repeats):
    """
    Run multiple k-coloring algorithms on a list of graphs multiple times.
    
    Parameters
    ----------
    graphs : list
        A list of graphs, each in adjacency list representation. 
        E.g. [ [ [1,2], [0,2], [0,1] ], [ ... ], ... ]
        
    algorithms : list
        A list of callables (functions) that implement the k-coloring algorithm.
        Each algorithm should accept a graph (adjacency list) and return:
        (coloring_list, k) where:
            coloring_list : list of integers representing the assigned color of each node.
            k : integer, number of colors used.
            
    repeats : int
        Number of times to run each algorithm on each graph.
        
    Returns
    -------
    dict
        A results dictionary structured to facilitate visualization with Recharts.
        
        Structure:
        {
          "graphs": [
            {
              "graph_id": <int>,
              "graph_data": <the graph adjacency list>,
              "algorithms": [
                {
                  "name": <algorithm_name>,
                  "runs": [
                    {
                      "run_id": <int>,
                      "runtime": <float>,
                      "memory": <int>,
                      "k": <int>,
                      "coloring": <list of colors per node>
                    }, ...
                  ],
                  "aggregate": {
                    "runtime": {"avg": float, "std": float, "min": float, "max": float},
                    "memory": {"avg": float, "std": float, "min": float, "max": float},
                    "k": {"avg": float, "std": float, "min": float, "max": float}
                  }
                }, ...
              ]
            }, ...
          ]
        }
    """

    results = {
        "graphs": []
    }
    algorithms = valid_algorithms()


    for graph_idx, graph in enumerate(graphs):
        if "chromatic_number" in graph.keys():     
            chromatic_number = graph['chromatic_number']
        else:
            chromatic_number = None
        graph_entry = {
            "graph_id": graph_idx,
            "graph_data": graph['graph'],
            "chromatic_number": chromatic_number,
            "algorithms": []
        }
        graph_adj = graph['graph']
        print("graph_adj", graph_adj)
        
        for algorithm_name in algorithm_names:
            algorithm = algorithms[algorithm_name]
            runtimes = []
            memories = []
            colors_used = []
            runs_data = []

            for run_id in range(repeats):
                # Measure runtime
                res_obj, runtime = measure_runtime(algorithm, graph_adj)
                k = len(set(res_obj['coloring'].values()))
                # Measure memory
                res_obj_mem, peak_memory = measure_memory(algorithm, graph_adj)
                
                # assume coloring and k are consistent from both runtime and memory calls
                # If they differ, prioritize runtime call results.
                # For simplicity, just use the first call's results.
                runs_data.append({
                    "run_id": run_id,
                    "runtime": runtime,
                    "memory": peak_memory,
                    "k": k,
                    "coloring": res_obj['coloring']
                })
                runtimes.append(runtime)
                memories.append(peak_memory)
                colors_used.append(k)

            # Compute statistics
            def compute_stats(values):
                return {
                    "avg": statistics.mean(values),
                    "std": statistics.pstdev(values) if len(values) > 1 else 0.0,
                    "min": min(values),
                    "max": max(values)
                }
            
            algo_entry = {
                "name": algorithm_name,
                "runs": runs_data,
                "aggregate": {
                    "runtime": compute_stats(runtimes),
                    "memory": compute_stats(memories),
                    "k": compute_stats(colors_used)
                }
            }
            
            graph_entry["algorithms"].append(algo_entry)
        
        results["graphs"].append(graph_entry)
    
    return results