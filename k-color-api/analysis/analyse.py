import math
import statistics
from scipy.stats import ttest_ind
from analysis.measurements import measure_runtime, measure_memory
from utils.validation import valid_algorithms

def sanitize_for_json(obj):
    if isinstance(obj, float):
        # Replace NaN or infinite values with None.
        if math.isnan(obj) or math.isinf(obj):
            return None
        else:
            return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(i) for i in obj]
    else:
        return obj
    

def compute_confidence_interval(values, confidence=0.95):
    n = len(values)
    avg = statistics.mean(values)
    if n < 2:
        return (avg, avg)
    std = statistics.pstdev(values)
    z = 1.96  # Approximate z-score for 95% CI
    margin = z * (std / math.sqrt(n))
    return (avg - margin, avg + margin)

def compute_stats(values):
    avg = statistics.mean(values)
    std = statistics.pstdev(values) if len(values) > 1 else 0.0
    return {
        "avg": avg,
        "std": std,
        "min": min(values),
        "max": max(values),
        "ci": compute_confidence_interval(values)
    }

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
        chromatic_number = graph.get('chromatic_number', None)
        graph_entry = {
            "graph_id": graph_idx,
            "graph_data": graph['graph'],
            "chromatic_number": chromatic_number,
            "algorithms": []
        }
        graph_adj = graph['graph']
        
        for algorithm_name in algorithm_names:
            algorithm = algorithms[algorithm_name]
            runtimes = []
            memories = []
            colors_used = []
            runs_data = []

            for run_id in range(repeats):
                print(algorithm_name, "run", run_id, "starting")
                res_obj, runtime, peak_memory = measure_runtime(algorithm, graph_adj)
                k = len(set(res_obj['coloring'].values()))
                print("Run", run_id, "of", algorithm_name, "Complete in", runtime, "seconds")
                
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
        
        # Perform pairwise t-tests between all algorithm pairs for this graph.
        comparisons = []
        algs = graph_entry["algorithms"]
        for i in range(len(algs)):
            for j in range(i + 1, len(algs)):
                alg1 = algs[i]
                alg2 = algs[j]
                runtime_ttest = ttest_ind(
                    [r["runtime"] for r in alg1["runs"]],
                    [r["runtime"] for r in alg2["runs"]],
                    equal_var=False
                )
                memory_ttest = ttest_ind(
                    [r["memory"] for r in alg1["runs"]],
                    [r["memory"] for r in alg2["runs"]],
                    equal_var=False
                )
                k_ttest = ttest_ind(
                    [r["k"] for r in alg1["runs"]],
                    [r["k"] for r in alg2["runs"]],
                    equal_var=False
                )
                comparisons.append({
                    "algorithms": [alg1["name"], alg2["name"]],
                    "runtime": {
                        "t_stat": runtime_ttest.statistic,
                        "p_value": runtime_ttest.pvalue
                    },
                    "memory": {
                        "t_stat": memory_ttest.statistic,
                        "p_value": memory_ttest.pvalue
                    },
                    "k": {
                        "t_stat": k_ttest.statistic,
                        "p_value": k_ttest.pvalue
                    }
                })
        graph_entry["statistical_tests"] = comparisons
        results["graphs"].append(graph_entry)
    
    return sanitize_for_json(results)
