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

def backtrack_coloring(node_index, graph, k, coloring, nodes_ordered, steps, record_steps=True):
    """
    Recursively attempt to assign colors to each node using backtracking.
    
    Parameters:
      - node_index: The current index in the ordered list of nodes.
      - graph: The adjacency list of the graph.
      - k: The number of colors being tried.
      - coloring: The current color assignment (a dict mapping node -> color).
      - nodes_ordered: A list of nodes ordered (e.g. by descending degree) to optimize backtracking.
      - steps: A list to record the step-by-step actions (if record_steps is True).
      - record_steps: Boolean flag indicating whether to record steps.
      
    Returns:
      - True if a valid coloring is found, False otherwise.
    """
    # If all nodes have been considered, we're done.
    if node_index == len(nodes_ordered):
        return True

    current_node = nodes_ordered[node_index]

    # If the node already has an assigned color (from the initial assignment),
    # simply skip to the next node.
    if current_node in coloring:
        return backtrack_coloring(node_index + 1, graph, k, coloring, nodes_ordered, steps, record_steps)

    # Try all possible colors for the current node.
    for color in range(1, k + 1):
        if is_safe(current_node, color, graph, coloring):
            coloring[current_node] = color  # Assign the color
            if record_steps:
                steps.append(coloring.copy())
            if backtrack_coloring(node_index + 1, graph, k, coloring, nodes_ordered, steps, record_steps):
                return True  # Found a valid coloring
            # Backtrack: remove the color assignment.
            del coloring[current_node]
            if record_steps:
                steps.append(coloring.copy())
    if record_steps:
        steps.append(coloring.copy())
    return False  # No valid color found for this node

def find_min_k_backtracking(graph, k=1, record_steps=False, initial_assignment=None):
    """
    Find the minimum number of colors needed to color the graph, optionally starting with
    an initial assignment.

    Parameters:
      - graph: The adjacency list of the graph.
      - k: The starting number of colors to try (default is 1).
      - record_steps: Boolean indicating whether to record the step-by-step actions.
      - initial_assignment: Optional dictionary mapping some nodes to pre-assigned colors.

    Returns:
      - A dictionary (based on algorithmResultTemplate) with the following keys:
          - 'chromatic_number': The minimal number of colors found.
          - 'k': The value of k used.
          - 'coloring': A dictionary mapping nodes to colors.
          - 'steps': A list of step-by-step actions (if record_steps is True).
    """
    res_obj = algorithmResultTemplate.copy()
    nodes = list(graph.keys())
    
    # Optional Optimization: Order nodes by descending degree.
    nodes_ordered = sorted(nodes, key=lambda x: len(graph[x]), reverse=True)
    
    # Start with the initial assignment if provided.
    if initial_assignment is not None:
        coloring = initial_assignment.copy()
        # Ensure k is at least as large as the highest color already used.
        max_initial = max(initial_assignment.values()) if initial_assignment else 1
        if k < max_initial:
            k = max_initial
    else:
        coloring = {}
    steps_list = []
    while True:
        # Attempt to color the graph starting from the current (possibly pre-colored) assignment.
        if backtrack_coloring(0, graph, k, coloring, nodes_ordered, steps_list, record_steps):
            res_obj['chromatic_number'] = k
            res_obj['k'] = k
            if record_steps:
                # Optionally record the final coloring as the last step.
                steps_list.append(coloring.copy())
                res_obj['steps'] = steps_list
            res_obj['coloring'] = coloring
            return res_obj
        # Increase the number of colors and try again.
        k += 1
