import math 

def ND_to_NE(N, D):
    if D <= 0 or D >= 1:
        raise ValueError("Graph density must be between 0 and 1 (non-inclusive).")
    
    max_edges = N * (N - 1) // 2
    E = int(max_edges * D)
    if E < N - 1:
        E = N - 1  # Ensure the graph can be connected
    return N, E

def DE_to_NE(E, D):
    """
    Calculate the minimum number of nodes required in a simple undirected graph
    given the number of edges and the desired density.

    Parameters:
    - E (int): The number of edges in the graph. Must be non-negative.
    - D (float): The desired density of the graph (0 < D < 1).

    Returns:
    - int: The minimum number of nodes required.

    Raises:
    - ValueError: If inputs are invalid.
    """
    if not isinstance(E, int) or E < 0:
        raise ValueError("Number of edges must be a non-negative integer.")
    
    if not isinstance(D, (float, int)) or not (0 < D < 1):
        raise ValueError("Graph density must be between 0 and 1 (non-inclusive).")
    
    if E == 0:
        return 1  # At least one node is needed even with zero edges

    # Derive the quadratic equation: n^2 - n - (2E/D) = 0
    discriminant = 1 + (8 * E) / D
    sqrt_discriminant = math.sqrt(discriminant)
    n = (1 + sqrt_discriminant) / 2

    # Ceiling to ensure enough nodes
    required_nodes = math.ceil(n)

    # Verify the density condition
    while True:
        max_possible_edges = required_nodes * (required_nodes - 1) / 2
        actual_density = E / max_possible_edges
        if actual_density <= D:
            break
        required_nodes += 1

    return required_nodes, E

def calculate_graph_metrics(adjacency_dict):
    """
    Calculates various graph metrics from an adjacency dictionary.

    Parameters:
    - adjacency_dict (dict): Adjacency list of the graph where keys are node identifiers
      and values are lists of adjacent nodes.

    Returns:
    - dict: A dictionary containing metrics like number of nodes, edges, density,
      average edges per node, degree distribution, and connected components.
    """
    nodes = len(adjacency_dict)
    edges_set = set()
    total_degree = 0
    degree_distribution = {}

    for node, neighbors in adjacency_dict.items():
        degree = len(neighbors)
        degree_distribution[node] = degree
        total_degree += degree
        for neighbor in neighbors:
            edge = tuple(sorted([node, neighbor]))
            edges_set.add(edge)

    edges = len(edges_set)
    density = (2 * edges) / (nodes * (nodes - 1)) if nodes > 1 else 0
    average_edges_per_node = total_degree / nodes if nodes > 0 else 0

    connected_components = num_connected_components(adjacency_dict)

    return {
        'nodes': nodes,
        'edges': edges,
        'density': round(density, 4),
        'average_edges_per_node': round(average_edges_per_node, 2),
        'degree_distribution': degree_distribution,
        'connected_components': connected_components
    }

def num_connected_components(adjacency_dict):
    # Calculate connected components using DFS
    visited = set()
    connected_components = 0

    def dfs(current_node):
        stack = [current_node]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                stack.extend([n for n in adjacency_dict[node] if n not in visited])

    for node in adjacency_dict:
        if node not in visited:
            dfs(node)
            connected_components += 1
    return connected_components