import time
from collections import defaultdict
from .algorithmResult import algorithmResultTemplate

def is_safe(node, color, graph, coloring):
    """
    Check if it is safe to assign 'color' to 'node' given the current partial coloring.
    A color is safe if no adjacent node already has that color.
    """
    for neighbour in graph[node]:
        if coloring.get(neighbour, 0) == color:
            return False
    return True

def backtrack_dsatur_coloring(graph, k, coloring, record_steps, steps):
    """
    Recursively try to assign colors (from 1 to k) to all uncolored nodes using
    a DSATUR-based dynamic ordering: at each call, pick the uncolored node with
    the highest saturation (number of different colors among its neighbors) and,
    in case of ties, the highest degree.
    
    Parameters:
      - graph: dict, the adjacency list.
      - k: int, the maximum color allowed (we try to color with colors 1..k).
      - coloring: dict, the current color assignment (pre-assigned nodes remain fixed).
                  Uncolored nodes should have value 0.
      - record_steps: bool, whether to record each coloring step.
      - steps: list, a list to record intermediate colorings (if record_steps is True).
      
    Returns:
      - True if a valid complete coloring is found using colors 1..k, False otherwise.
    """
    # Base case: if every node is colored (nonzero), we have a complete coloring.
    if all(coloring[node] != 0 for node in graph):
        return True

    # Determine the list of uncolored nodes.
    uncolored = [node for node in graph if coloring[node] == 0]

    # Compute the saturation for each uncolored node:
    # Saturation is the number of distinct colors already used by its neighbors.
    saturation = {}
    for node in uncolored:
        used_colors = {coloring[neighbor] for neighbor in graph[node] if coloring[neighbor] != 0}
        saturation[node] = len(used_colors)

    # Choose the next node using DSATUR ordering:
    # Pick the uncolored node with the highest saturation; break ties by selecting the one with the highest degree.
    next_node = max(uncolored, key=lambda v: (saturation[v], len(graph[v])))

    # Try every color from 1 to k for the selected node.
    for c in range(1, k + 1):
        if is_safe(next_node, c, graph, coloring):
            coloring[next_node] = c
            if record_steps:
                steps.append(coloring.copy())
            if backtrack_dsatur_coloring(graph, k, coloring, record_steps, steps):
                return True
            # Backtrack
            coloring[next_node] = 0
            if record_steps:
                steps.append(coloring.copy())
    return False

def find_min_k_backtracking_dsatur(graph, k=1, record_steps=False, initial_assignment=None):
    """
    Attempts to find a valid coloring of the graph using the minimum number of colors,
    combining backtracking with DSATUR ordering. At each recursive call, the next vertex
    chosen is the one with highest saturation (and degree as tie-breaker). An optional
    initial_assignment (a dict mapping node -> color) may be provided; these assignments
    are treated as fixed.

    Parameters:
      - graph: dict, the adjacency list of the graph.
      - k: int, the starting number of colors to try (default is 1).
      - record_steps: bool, if True, record all intermediate coloring states.
      - initial_assignment: dict or None, pre-assigned colors (e.g., {node: color, ...}).
    
    Returns:
      A dict (based on algorithmResultTemplate) with keys:
         - "chromatic_number": the minimal number of colors found (largest color in the solution).
         - "k": same as chromatic_number.
         - "runtime (s)": elapsed time in seconds.
         - "steps": a list of intermediate colorings (if record_steps=True).
         - "coloring": the final complete coloring (a dict mapping node -> color).
    """
    res_obj = algorithmResultTemplate.copy()
    start_time = time.time()

    # Build a base coloring:
    # Nodes in the initial_assignment (if any) get their fixed color;
    # all other nodes start uncolored (denoted by 0).
    base_coloring = {}
    for node in graph:
        if initial_assignment is not None and node in initial_assignment:
            base_coloring[node] = initial_assignment[node]
        else:
            base_coloring[node] = 0

    # Ensure that k is at least as high as the maximum fixed color.
    if initial_assignment:
        max_fixed = max(initial_assignment.values())
        if k < max_fixed:
            k = max_fixed

    steps_list = []

    # We try increasing values of k until a complete coloring is found.
    while True:
        # Start fresh from the base (fixed) coloring.
        coloring = base_coloring.copy()
        if backtrack_dsatur_coloring(graph, k, coloring, record_steps, steps_list):
            end_time = time.time()
            res_obj['chromatic_number'] = k
            res_obj['k'] = k
            res_obj['runtime (s)'] = end_time - start_time
            if record_steps:
                steps_list.append(coloring.copy())
                res_obj['steps'] = steps_list
            else:
                res_obj['steps'] = [coloring.copy()]

            res_obj['coloring'] = coloring.copy()
            return res_obj
        # Increase k and try again.
        k += 1
