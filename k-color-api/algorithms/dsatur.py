import time
from collections import defaultdict
from .algorithmResult import algorithmResultTemplate

def dsatur_coloring(graph, record_steps=False, initial_assignment=None, k = None):
    """
    Performs graph coloring using the DSATUR (Degree of Saturation) heuristic.
    Optionally accepts an initial coloring (a dict mapping node -> color) that will be
    preserved while coloring the remaining nodes.
    
    :param graph: dict, adjacency list of the graph (e.g. {node: [neighbors], ...})
    :param record_steps: bool, if True, record partial colorings at each assignment.
    :param initial_coloring: dict or None, optional pre-assigned colors (e.g. {node: color, ...}).
                             Colors should be positive integers. Nodes not provided will be colored.
    :param k irrelevent only there for compatability with graph coloring
    :return: a dict (based on algorithmResultTemplate) with keys:
             "chromatic_number", "k", "runtime (s)", "steps", "coloring"
    """

    # Copy the template so we don't overwrite the original
    res_obj = algorithmResultTemplate.copy()
    
    # Start timing
    start_time = time.time()
    
    # Check for self-loops which make coloring impossible
    for node, neighbors in graph.items():
        if node in neighbors:
            # Self-loop detected => no proper coloring is possible
            return None

    # Handle empty graph
    if not graph:
        end_time = time.time()
        res_obj["chromatic_number"] = 0
        res_obj["k"] = 0
        res_obj["runtime (s)"] = end_time - start_time
        res_obj["steps"] = []
        res_obj["coloring"] = {}
        return res_obj

    # Initialize coloring: if an initial coloring is provided, use it; otherwise mark uncolored as 0.
    color = {}
    for node in graph:
        if initial_assignment is not None and node in initial_assignment:
            color[node] = initial_assignment[node]
        else:
            color[node] = 0

    # Determine which nodes still need to be colored.
    uncolored_nodes = set(node for node in graph if color[node] == 0)

    # Initialize helper structure: for each uncolored node, record the set of colors used by its colored neighbors.
    neighbor_colors_used = defaultdict(set)
    for node in graph:
        if color[node] != 0:
            for nbr in graph[node]:
                # Only update for uncolored neighbors.
                if nbr in uncolored_nodes:
                    neighbor_colors_used[nbr].add(color[node])
    
    # Initialize saturation values for each uncolored node.
    saturation = defaultdict(int)
    for node in uncolored_nodes:
        saturation[node] = len(neighbor_colors_used[node])
    
    # Precompute degrees (needed to break ties in saturation)
    degrees = {}
    for node, neighbors in graph.items():
        degrees[node] = len(neighbors)
    
    steps = []  # To store intermediate steps if record_steps is True
    if record_steps:
        steps.append(color.copy())

    # DSATUR main loop:
    while uncolored_nodes:
        # 1) Choose the vertex with the largest saturation; tie-break on degree.
        current_node = max(uncolored_nodes, key=lambda v: (saturation[v], degrees[v]))

        # 2) Find the smallest color not in neighbor_colors_used[current_node].
        used_by_neighbors = neighbor_colors_used[current_node]
        c = 1
        while c in used_by_neighbors:
            c += 1
        
        # Assign color to the current node.
        color[current_node] = c
        
        # 3) Remove current_node from uncolored set.
        uncolored_nodes.remove(current_node)

        # 4) Update saturation for each uncolored neighbor.
        for nbr in graph[current_node]:
            if nbr in uncolored_nodes:
                if c not in neighbor_colors_used[nbr]:
                    neighbor_colors_used[nbr].add(c)
                    saturation[nbr] = len(neighbor_colors_used[nbr])
        
        # 5) Record the coloring step if required.
        if record_steps:
            steps.append(color.copy())

    # End timing
    end_time = time.time()

    # The chromatic number is the maximum color used.
    max_color = max(color.values())
    
    # Populate result object.
    res_obj["k"] = max_color
    res_obj["chromatic_number"] = max_color
    res_obj["runtime (s)"] = end_time - start_time
    res_obj["steps"] = steps if record_steps else []
    res_obj["coloring"] = color.copy()

    return res_obj
