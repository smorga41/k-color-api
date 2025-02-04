import time

from collections import defaultdict
from .algorithmResult import algorithmResultTemplate

def dsatur_coloring(graph, record_steps=False):
    """
    Performs graph coloring using the DSATUR (Degree of Saturation) heuristic.
    
    :param graph: dict, adjacency list of the graph (e.g. {1: [2,3], 2: [1], 3: [1], ...})
    :param record_steps: bool, if True, record partial colorings at each assignment.
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

    # All nodes initially uncolored => color[node] = 0
    color = {}
    for node in graph:
        color[node] = 0

    # Saturation: how many distinct neighbor-colors a node has
    saturation = defaultdict(int)
    # A helper structure that keeps track of which colors neighbors of a node are currently using
    neighbor_colors_used = defaultdict(set)
    
    # Precompute degrees (needed to break ties in saturation)
    degrees = {}
    for node, neighbors in graph.items():
        degrees[node] = len(neighbors)
    
    # List (or set) of uncolored vertices
    uncolored_nodes = set(graph.keys())

    # Initialize saturations (all zero at the start)
    for node in uncolored_nodes:
        saturation[node] = 0

    steps = []  # To store intermediate steps if record_steps is True

    # DSATUR main loop:
    while uncolored_nodes:
        # 1) Choose the vertex with the largest saturation; tie-break on degree
        #    max by (saturation[v], degrees[v])
        current_node = max(uncolored_nodes, key=lambda v: (saturation[v], degrees[v]))

        # 2) Find the smallest color not in neighbor_colors_used[current_node]
        used_by_neighbors = neighbor_colors_used[current_node]
        c = 1
        while c in used_by_neighbors:
            c += 1
        
        # Assign color
        color[current_node] = c
        
        # 3) Remove current_node from uncolored set
        uncolored_nodes.remove(current_node)

        # 4) Update saturation for neighbors
        for nbr in graph[current_node]:
            if color[nbr] == 0:  # only if neighbor is uncolored
                if c not in neighbor_colors_used[nbr]:
                    neighbor_colors_used[nbr].add(c)
                    saturation[nbr] += 1

        # 5) Record the coloring step if required
        if record_steps:
            # Create a shallow copy of the current coloring state
            steps.append(dict(color))

    # End timing
    end_time = time.time()

    # The chromatic number (or the number of colors used) is the max color assigned
    max_color = max(color.values())
    
    # Populate result object
    res_obj["k"] = max_color
    res_obj["runtime (s)"] = end_time - start_time
    res_obj["steps"] = steps if record_steps else []
    res_obj["coloring"] = color.copy()

    return res_obj
