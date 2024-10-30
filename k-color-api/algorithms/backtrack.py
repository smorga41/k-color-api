from .algorithmResult import algorithmResultTemplate

def is_safe(node, color, graph, coloring):
    """
    Check if it's safe to assign the given color to the node.
    A color is safe if no adjacent node has the same color.
    """
    for neighbour in graph[node]:
        if neighbour in coloring and coloring[neighbour] == color:
            return False
    return True

def backtrack_coloring(node_index, graph, k, coloring, nodes_ordered, steps):
    """
    Recursively attempt to assign colors to each node using backtracking.
    
    Parameters:
    - node_index: The current index in the ordered list of nodes.
    - graph: The adjacency list of the graph.
    - k: The current number of colors being tried.
    - coloring: The current color assignment for nodes.
    - nodes_ordered: Nodes ordered (e.g., by descending degree) to optimize backtracking.
    - steps: List to store step-by-step actions.
    
    Returns:
    - True if a valid coloring is found, False otherwise.
    """
    if node_index == len(nodes_ordered):
        return True  # All nodes are colored successfully

    current_node = nodes_ordered[node_index]
    # steps.append(coloring.copy())

    for color in range(1, k + 1):
        if is_safe(current_node, color, graph, coloring):
            coloring[current_node] = color  # Assign color
            steps.append(coloring.copy())


            if backtrack_coloring(node_index + 1, graph, k, coloring, nodes_ordered, steps):
                return True  # Successful coloring

            # Backtrack
            del coloring[current_node]
            steps.append(coloring.copy())

    steps.append(coloring.copy())
    return False  # No valid color found for this node

def find_min_k_backtracking(graph, record_steps=True):
    """
    Find the minimum number of colors needed to color the graph.
    
    Parameters:
    - graph: The adjacency list of the graph.
    - record_steps: Boolean indicating whether to record steps.
    
    Returns:
    - A tuple (k, coloring, steps) where:
        - k is the minimal number of colors,
        - coloring is a dictionary mapping nodes to colors,
        - steps is a list of step-by-step actions (empty if record_steps is False).
    """
    res_obj = algorithmResultTemplate.copy()
    nodes = list(graph.keys())
    
    # Optional Optimization: Order nodes by descending degree
    nodes_ordered = sorted(nodes, key=lambda x: len(graph[x]), reverse=True)
    
    k = 1  # Start with one color
    # steps = []
    while True:
        coloring = {}
        steps = [] if record_steps else None
        if backtrack_coloring(0, graph, k, coloring, nodes_ordered, steps):
            res_obj['chromatic_number'] = k
            if record_steps:
                res_obj['steps'] = steps
            res_obj['steps'].append(coloring) 

            return res_obj
        # steps.append(steps)
        k += 1  # Try next number of colors
