import time
import math
import random
from collections import defaultdict
from .algorithmResult import algorithmResultTemplate  # Assuming this is defined elsewhere

def metropolis_coloring(graph, record_steps=False):
    """
    Performs graph coloring using the Metropolis algorithm (Glauber dynamics).
    
    The algorithm produces a uniformly random proper q-coloring of the graph G,
    given that q > 4*Delta (where Delta is the maximum degree of G). The final
    coloring is obtained after T = ceil(q * n * ln(2n) / (q - 4*Delta)) iterations.
    
    Parameters:
        graph (dict): Adjacency list representation of the graph.
                      Example: {1: [2, 3], 2: [1, 4], 3: [1], 4: [2]}
        q (int): The number of colors. Must satisfy q > 4 * Delta.
        record_steps (bool): If True, record and return intermediate colorings.
    
    Returns:
        dict: A result object with the following keys:
            - "k": the maximum color used in the final coloring (note that not all q colors
                   need be used),
            - "runtime (s)": the total runtime of the algorithm,
            - "steps": a list of intermediate colorings (if record_steps is True),
            - "coloring": the final coloring (a dict mapping vertices to colors),
            - "chromatic_number": None (since the algorithm produces a q-coloring, not necessarily
                                  an optimal or minimum coloring).
    """
    q = choose_q(graph)
    # Copy the algorithm result template so as not to modify the original.
    res_obj = algorithmResultTemplate.copy()
    
    start_time = time.time()
    
    # Check for self-loops (which would render proper coloring impossible).
    for v, neighbors in graph.items():
        if v in neighbors:
            # Self-loop detected => no proper coloring is possible.
            raise ValueError("Self-loop detected at vertex {}. No proper coloring possible.".format(v))
    
    n = len(graph)
    if n == 0:
        end_time = time.time()
        res_obj["chromatic_number"] = 0
        res_obj["k"] = 0
        res_obj["runtime (s)"] = end_time - start_time
        res_obj["steps"] = []
        res_obj["coloring"] = {}
        return res_obj

    # Compute the maximum degree Δ of the graph.
    Delta = max(len(neighbors) for neighbors in graph.values())
    
    # Ensure the condition q > 4*Delta is met.
    if q <= 4 * Delta:
        raise ValueError("Parameter q must be greater than 4 times the maximum degree (q > 4Δ).")
    
    # Compute the number of iterations T = ceil( q * n * ln(2n) / (q - 4Δ) ).
    T = math.ceil(q * n * math.log(2 * n) / (q - 4 * Delta))
    
    # Initialize an initial proper q-coloring f0 using a greedy algorithm.
    f = {}
    for v in graph:
        used_colors = set()
        for nbr in graph[v]:
            if nbr in f:
                used_colors.add(f[nbr])
        # Since q > Δ + 1, there is always an available color.
        for color in range(1, q + 1):
            if color not in used_colors:
                f[v] = color
                break

    steps = []
    if record_steps:
        steps.append(f.copy())

    # Main loop: perform T iterations of random recoloring.
    vertices = list(graph.keys())
    for t in range(1, T + 1):
        # Pick a random vertex.
        v = random.choice(vertices)
        # Pick a random color uniformly from 1 to q.
        c = random.randint(1, q)
        # Check if c does not appear among the colors of v's neighbours.
        neighbor_colors = {f[nbr] for nbr in graph[v]}
        if c not in neighbor_colors:
            f[v] = c
        if record_steps:
            steps.append(f.copy())

    end_time = time.time()
    
    # Determine the maximum color used in the final coloring.
    used_colors = set(f.values())
    k_used = len(used_colors)
    
    # Populate the result object.
    res_obj["k"] = k_used
    res_obj["runtime (s)"] = end_time - start_time
    res_obj["steps"] = steps if record_steps else []
    res_obj["coloring"] = f.copy()
    res_obj["chromatic_number"] = None  # This algorithm produces a q-coloring, not necessarily a minimal one.

    return res_obj

def choose_q(graph):
    # Compute maximum degree Δ of the graph.
    Delta = max(len(neighbors) for neighbors in graph.values())
    # Choose q to be 4Δ + 1 (this satisfies q > 4Δ)
    q = 4 * Delta + 1
    return q
