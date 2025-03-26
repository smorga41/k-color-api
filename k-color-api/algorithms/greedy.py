import random
from .algorithmResult import algorithmResultTemplate
from collections import deque

def greedy_bfs_coloring(graph, record_steps=False):
    """
    Performs greedy coloring of the graph using BFS traversal.
    A random starting node is chosen each time. Assumes the graph is connected.
    
    :param graph: dict, adjacency list of the graph.
    :param record_steps: bool, if True records the coloring after each node is colored.
    :return: dict with keys 'coloring', 'k' (number of colors used), and optionally 'steps',
             or None if a self-loop is detected.
    """
    res_obj = algorithmResultTemplate.copy()
    steps = []
    
    # Check for self-loops.
    for node, neighbors in graph.items():
        if node in neighbors:
            return None

    coloring = {}
    nodes = list(graph.keys())
    if not nodes:
        return res_obj  # Empty graph, return empty result

    # Choose a random start node.
    start = random.choice(nodes)
    bfs_queue = deque([start])
    visited = {start}
    
    while bfs_queue:
        current_node = bfs_queue.popleft()
        # Determine colors used by neighbors that have already been colored.
        neighbor_colors = {coloring[neighbor] for neighbor in graph[current_node] if neighbor in coloring}
        # Assign the smallest available color.
        color = 1
        while color in neighbor_colors:
            color += 1
        coloring[current_node] = color
        if record_steps:
            steps.append(coloring.copy())
        # Enqueue unvisited neighbors.
        for neighbor in graph[current_node]:
            if neighbor not in visited:
                visited.add(neighbor)
                bfs_queue.append(neighbor)

    res_obj['coloring'] = coloring.copy()
    res_obj['k'] = len(set(coloring.values()))
    if record_steps:
        res_obj['steps'] = steps

    return res_obj


def welsh_powell_coloring(graph, record_steps=False):
    """
    Performs Welsh-Powell greedy coloring of the graph, sorting nodes by decreasing degree.
    :param graph: dict, adjacency list of the graph
    :param record_steps: bool, flag to record intermediate coloring steps
    :return: dict containing 'coloring', 'k' colors used, and optional 'steps'
    """
    res_obj = algorithmResultTemplate.copy()

    # Check for self-loops
    for node, neighbors in graph.items():
        if node in neighbors:
            return None

    # Sort nodes by decreasing degree
    nodes_sorted = sorted(graph.keys(), key=lambda node: len(graph[node]), reverse=True)

    coloring = {}

    for node in nodes_sorted:
        neighbor_colors = {coloring[neighbor] for neighbor in graph[node] if neighbor in coloring}

        # Assign the smallest available color
        color = 1
        while color in neighbor_colors:
            color += 1

        coloring[node] = color

        if record_steps:
            res_obj['steps'].append(coloring.copy())

    res_obj['coloring'] = coloring
    res_obj['k'] = len(list(set(coloring.values())))

    return res_obj



def greedy_coloring(graph, record_steps=False):
    """
    Performs greedy coloring of the graph.
    :param graph: dict, adjacency list of the graph
    :param record_steps: bool, if True records the coloring after each node is colored
    :return: dict with keys 'coloring', 'k' (number of colors used), and optionally 'steps'
             or None if a self-loop is detected.
    """
    # Prepare result template (assumes algorithmResultTemplate exists)
    print("GREEEDY")
    res_obj = algorithmResultTemplate.copy()
    
    # Check for self-loops
    for node, neighbors in graph.items():
        if node in neighbors:
            return None

    coloring = {}
    nodes = list(graph.keys())
    random.shuffle(nodes)
    steps = [] if record_steps else None

    for node in nodes:
        # Use a set comprehension to quickly gather colors of already-colored neighbors.
        neighbor_colors = {coloring[neighbor] for neighbor in graph[node] if neighbor in coloring}
        
        # Find the smallest available color.
        # Instead of creating a candidate set, we iterate until we find a color not used.
        color = 1
        while color in neighbor_colors:
            color += 1
        coloring[node] = color

        if record_steps:
            steps.append(coloring.copy())
    
    res_obj['coloring'] = coloring.copy()
    res_obj['k'] = len(set(coloring.values()))
    if record_steps:
        res_obj['steps'] = steps

    return res_obj