from .algorithmResult import algorithmResultTemplate
from collections import deque

def greedy_bfs_coloring(graph):
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
    bfs_queue = deque([nodes[0]])  # Start from the first node in the list
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
        steps.append(coloring.copy())

    # Store the result in the template
    res_obj['steps'] = steps
    return res_obj


def greedy_coloring(graph):
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
    for node in nodes:
        # Get colors used by neighbors
        neighbor_colors = set()
        for neighbor in graph[node]:
            if neighbor in coloring:
                neighbor_colors.add(coloring[neighbor])
            elif neighbor not in graph:
                # Node not in graph, ignore or handle as needed
                continue

        # Assign the smallest available color
        color = 1
        while color in neighbor_colors:
            color += 1
        coloring[node] = color
        steps.append(coloring.copy())
         

    res_obj['steps'] = steps
    return res_obj