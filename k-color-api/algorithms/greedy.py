import random
from .algorithmResult import algorithmResultTemplate
from collections import deque

def greedy_bfs_coloring(graph, record_steps=False):
    """
    Performs greedy coloring of the graph using BFS traversal.
    :param graph: dict, adjacency list of the graph
    :return: dict of node colors or None if coloring is not possible
    """
    res_obj = algorithmResultTemplate.copy()

    steps = []

    # Check for self-loops
    for node, neighbors in graph.items():
        if node in neighbors:
            # Self-loop detected
            return None

    # Greedy coloring using BFS
    coloring = {}
    nodes = list(graph.keys())
    if not nodes:
        return res_obj  # Empty graph, return empty result

    # Initialize BFS queue
    bfs_queue = deque([nodes[random.randint(0,len(nodes)-1)]])  # Start from a random node
    visited = set()
    visited.add(nodes[0])

    while bfs_queue:
        current_node = bfs_queue.popleft()
        neighbor_colors = set()

        # Find colors used by neighbors
        for neighbor in graph[current_node]:
            if neighbor in coloring:
                neighbor_colors.add(coloring[neighbor])
            if neighbor not in visited:
                visited.add(neighbor)
                bfs_queue.append(neighbor)

        # Assign the smallest available color
        color = 1
        while color in neighbor_colors:
            color += 1
        coloring[current_node] = color

        # Record the coloring step
        if record_steps:
            steps.append(coloring.copy())

    # Store the result in the template
    if record_steps:
        res_obj['steps'] = steps
    res_obj['coloring'] = coloring.copy()
    res_obj['k'] = len(list(set(coloring.values())))

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
    :return: dict of node colors or None if coloring is not possible
    """
    # Check for self-loops
    res_obj = algorithmResultTemplate.copy()

    steps = []
    for node, neighbors in graph.items():
        if node in neighbors:
            # Self-loop detected
            return None

    coloring = {}
    nodes = list(graph.keys())
    random.shuffle(nodes)
    for node in nodes:
        # Get colors used by neighbors
        # TODO use sets and intersection to make this more efficeint
        neighbor_colors = set()
        for neighbor in graph[node]:
            if str(neighbor) in coloring.keys():
                neighbor_colors.add(coloring[neighbor])
            elif neighbor not in graph:
                # Node not in graph, ignore or handle as needed
                continue

        # Assign the smallest available color
        color = 1
        while color in neighbor_colors:
            color += 1
        coloring[node] = color
    if record_steps:
        steps.append(coloring.copy())
         
    if record_steps:
        res_obj['steps'] = steps
    res_obj['k'] = len(list(set(coloring.values())))
    res_obj['coloring'] = coloring.copy()
    return res_obj