
def combine_scaling_result(data):
    """
    Transforms the experiment_result into a format suitable for combined charts.
    
    Args:
        data (dict): The original experiment_result with algorithms as top-level keys.
    
    Returns:
        dict: A dictionary containing 'chartData' and 'algorithms'.
    """
    algorithms = list(data.keys())

    if not algorithms:
        return {"chartData": [], "algorithms": []}

    # Extract all node sizes from the first algorithm
    first_algorithm = algorithms[0]
    node_sizes = sorted([int(ns) for ns in data[first_algorithm].keys()])

    chart_data = []
    for node_size in node_sizes:
        entry = {"nodeSize": node_size}
        for algorithm in algorithms:
            metrics = data[algorithm].get(node_size, {})
            entry[f"{algorithm}_avg_memory"] = metrics.get("avg_memory", None)
            entry[f"{algorithm}_std_memory"] = metrics.get("std_memory", None)
            entry[f"{algorithm}_avg_runtime"] = metrics.get("avg_runtime", None)
            entry[f"{algorithm}_std_runtime"] = metrics.get("std_runtime", None)
            # Include other metrics if needed
        chart_data.append(entry)

    return {"chartData": chart_data, "algorithms": algorithms}