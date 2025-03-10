from .algorithmResult import algorithmResultTemplate
import heapq

def is_safe(node, color, graph, coloring):
    """
    Check if it's safe to assign the given color to the node.
    A color is safe if no adjacent node has the same color.
    """
    for neighbour in graph[node]:
        if neighbour in coloring and coloring[neighbour] == color:
            return False
    return True

def greedy_extension(coloring, nodes_ordered, graph):
    """
    Greedily extend a partial coloring to a complete coloring.
    For each uncolored node (following the given order), assign the smallest safe color.
    Returns the total number of colors used in the greedy complete assignment.
    This value serves as a heuristic (upper bound) on the number of colors
    needed from this branch.
    """
    new_coloring = coloring.copy()
    current_max = max(new_coloring.values()) if new_coloring else 0
    for node in nodes_ordered:
        if node not in new_coloring:
            assigned = False
            for color in range(1, current_max + 1):
                if is_safe(node, color, graph, new_coloring):
                    new_coloring[node] = color
                    assigned = True
                    break
            if not assigned:
                new_coloring[node] = current_max + 1
                current_max += 1
    return current_max

def find_min_k_branch_and_bound(graph, k=None, record_steps=False, initial_assignment=None):
    """
    Find the minimum number of colors needed to color the graph using a branch-and-bound
    algorithm with best-first search. Supports an optional initial assignment and an optional
    known optimal number of colors (k).

    Parameters:
      - graph: The adjacency list of the graph.
      - k: Optional integer representing the known optimal chromatic number.
                 If provided, the algorithm prunes any branch that would exceed this number.
      - record_steps: Boolean indicating whether to record step-by-step actions.
      - initial_assignment: Optional dictionary mapping nodes to pre-assigned colors.

    Returns:
      - A dictionary (based on algorithmResultTemplate) with the following keys:
          - 'chromatic_number': The minimal number of colors found.
          - 'k': The value of k used.
          - 'coloring': A dictionary mapping nodes to colors.
          - 'steps': A list of step-by-step actions (if record_steps is True).
    """
    # Order nodes by descending degree for efficiency.
    nodes = list(graph.keys())
    nodes_ordered = sorted(nodes, key=lambda x: len(graph[x]), reverse=True)
    
    # Start with the initial assignment if provided.
    if initial_assignment is not None:
        coloring = initial_assignment.copy()
    else:
        coloring = {}
    steps_list = []
    if record_steps:
        steps_list.append(coloring.copy())
    
    # Set the best known upper bound.
    # If known_k is provided, use it; otherwise, initialize to worst-case (each node gets a unique color).
    best_chromatic = len(graph) + 1  
    best_solution = None
    best_steps = []
    
    # Priority queue for best-first search.
    # Each element is a tuple: (priority, counter, current_coloring, steps_list)
    # The priority is given by the greedy extension heuristic.
    counter = 0
    initial_priority = greedy_extension(coloring, nodes_ordered, graph)
    heap = [(initial_priority, counter, coloring, steps_list)]
    
    while heap:
        prio, _, current_coloring, current_steps = heapq.heappop(heap)
        
        # If the heuristic is no better than the best solution found, prune this branch.
        if prio >= best_chromatic:
            continue

        # Check if the coloring is complete.
        if len(current_coloring) == len(nodes):
            current_max = max(current_coloring.values()) if current_coloring else 0
            if current_max < best_chromatic:
                best_chromatic = current_max
                best_solution = current_coloring.copy()
                best_steps = current_steps.copy() if record_steps else []
                # Early exit if we've reached the known optimal.
                if k is not None and best_chromatic == k:
                    res_obj = algorithmResultTemplate.copy()
                    res_obj['chromatic_number'] = best_chromatic
                    res_obj['k'] = best_chromatic
                    res_obj['coloring'] = best_solution
                    if record_steps:
                        res_obj['steps'] = best_steps
                    return res_obj
            continue

        # Determine the next uncolored node (following the ordering).
        next_node = None
        for node in nodes_ordered:
            if node not in current_coloring:
                next_node = node
                break
        if next_node is None:
            continue  # This should not happen
        
        current_max = max(current_coloring.values()) if current_coloring else 0
        # Determine the maximum color to try:
        # We try existing colors (1..current_max) and possibly one new color (current_max+1),
        # but we do not exceed best_chromatic.
        max_color_to_try = min(current_max + 2, best_chromatic + 1)
        for color in range(1, max_color_to_try):
            if is_safe(next_node, color, graph, current_coloring):
                new_coloring = current_coloring.copy()
                new_coloring[next_node] = color
                new_steps = current_steps.copy()
                if record_steps:
                    new_steps.append(new_coloring.copy())
                new_priority = greedy_extension(new_coloring, nodes_ordered, graph)
                if new_priority < best_chromatic:
                    counter += 1
                    heapq.heappush(heap, (new_priority, counter, new_coloring, new_steps))
    
    # If no complete solution was found, return None.
    if best_solution is None:
        return None
    
    res_obj = algorithmResultTemplate.copy()
    res_obj['chromatic_number'] = best_chromatic
    res_obj['k'] = best_chromatic
    res_obj['coloring'] = best_solution
    if record_steps:
        res_obj['steps'] = best_steps
    return res_obj
