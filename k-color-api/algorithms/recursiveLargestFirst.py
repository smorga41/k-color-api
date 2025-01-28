import time
from collections import defaultdict
from .algorithmResult import algorithmResultTemplate

def rlf_coloring(graph, record_steps=False):
    """
    Performs graph coloring using the RLF (Recursive Largest First) heuristic.
    
    :param graph: dict, adjacency list of the graph 
                  (e.g. {0: [9,2,4,6], 1: [5,8,6], 2: [0,9], ...})
    :param record_steps: bool, if True, record partial colorings at each assignment.
    :return: a dictionary with keys:
       - "chromatic_number": the number of colors used
       - "k": same as chromatic_number
       - "runtime (s)": elapsed time in seconds
       - "steps": a list of intermediate color dictionaries (if record_steps=True)
       - "coloring": the final coloring dictionary {node: color}
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

    # Convert adjacency lists to sets for faster membership checks
    adjacency = {v: set(nbrs) for v, nbrs in graph.items()}

    # All nodes initially uncolored => color[node] = 0
    color = {node: 0 for node in graph}
    
    # Set of uncolored vertices
    uncolored = set(graph.keys())

    steps = []  # To store intermediate steps if record_steps is True

    # Helper to count how many neighbors a candidate vertex has in a given set
    def neighbors_in_set(v, some_set):
        return len(adjacency[v].intersection(some_set))

    # Current color index
    current_color = 0

    # RLF main loop: color all vertices
    while uncolored:
        current_color += 1
        
        # 1) Pick a vertex with maximum degree (within uncolored)
        #    "degree" here means adjacency restricted to the uncolored subgraph.
        seed = max(uncolored, key=lambda v: neighbors_in_set(v, uncolored))
        
        # Color this seed vertex
        color[seed] = current_color
        if record_steps:
            steps.append(dict(color))  # record partial coloring
        uncolored.remove(seed)
        
        # 2) Partition remaining uncolored into P (blocked) and Q (free)
        #    - P = neighbors of seed that are still uncolored
        #    - Q = uncolored \ P
        P = adjacency[seed].intersection(uncolored)
        Q = uncolored.difference(P)

        # 3) Extend this color class (current_color) with as many Q vertices as possible
        #    We pick from Q the vertex that is most adjacent to P, color it,
        #    then update P and Q accordingly.
        while Q:
            # Pick w in Q that has the largest number of neighbors in P
            w = max(Q, key=lambda v: neighbors_in_set(v, P))
            color[w] = current_color
            if record_steps:
                steps.append(dict(color))
            
            # Remove w from uncolored
            uncolored.remove(w)
            # Remove w from Q
            Q.remove(w)
            
            # w's uncolored neighbors
            w_neighbors_uncolored = adjacency[w].intersection(uncolored)
            
            # The neighbors of w that are in Q now become blocked ⇒ move from Q to P
            move_to_blocked = w_neighbors_uncolored.intersection(Q)
            P.update(move_to_blocked)
            Q.difference_update(move_to_blocked)

    # End timing
    end_time = time.time()

    # Number of colors used is the highest color index
    max_color_used = current_color
    
    # Populate result object
    res_obj["chromatic_number"] = max_color_used
    res_obj["k"] = max_color_used
    res_obj["runtime (s)"] = end_time - start_time
    res_obj["steps"] = steps if record_steps else []
    res_obj["coloring"] = dict(color)

    return res_obj
