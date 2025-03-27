import math
import statistics
import multiprocessing
import time
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

def init_worker():
    # Rename the process for clarity.
    multiprocessing.current_process().name = "TimeoutWorker"
    # Optionally, close or reinitialize non-pickleable resources here.

def run_with_timeout(func, args=(), kwargs={}, timeout=None):
    pool = multiprocessing.Pool(processes=1, initializer=init_worker)
    async_result = pool.apply_async(func, args, kwargs)
    try:
        result = async_result.get(timeout=timeout)
    except multiprocessing.TimeoutError:
        pool.terminate()
        pool.join()
        raise TimeoutError("Function call timed out")
    pool.close()
    pool.join()
    return result

def run_with_timeout_in_pool(pool, func, args=(), kwargs={}, timeout=None):
    async_result = pool.apply_async(func, args, kwargs)
    try:
        result = async_result.get(timeout=timeout)
    except multiprocessing.TimeoutError:
        raise TimeoutError("Function call timed out")
    return result


def run_coloring_experiment(graphs, algorithm_names, repeats, timeout=3):
    results = { "graphs": [] }
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
            print("ALgo", algorithm_name)
            algorithm = algorithms[algorithm_name]
            runtimes, memories, colors_used = [], [], []
            runs_data = []
            successful = True

            # Create a dedicated pool for this algorithm if timeout is enabled.
            pool = None
            if timeout is not None:
                pool = multiprocessing.Pool(processes=1, initializer=init_worker)

            for run_id in range(repeats):
                print(algorithm_name, "run", run_id, "starting")
                try:
                    if timeout is not None:
                        res_obj, runtime, peak_memory = run_with_timeout_in_pool(
                            pool, measure_runtime, args=(algorithm, graph_adj), timeout=timeout
                        )
                    else:
                        res_obj, runtime, peak_memory = measure_runtime(algorithm, graph_adj)
                except TimeoutError:
                    print(f"{algorithm_name} run {run_id} timed out after {timeout} seconds. Skipping further runs for this algorithm.")
                    successful = False
                    if pool is not None:
                        pool.terminate()
                        pool.join()
                    print("Finish error")
                    break  # Stop running this algorithm on the current graph

                k = len(set(res_obj['coloring'].values()))
                print("Run", run_id, "of", algorithm_name, "complete in", runtime, "seconds")
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

            if pool:
                pool.close()
                pool.join()

            if successful:
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

