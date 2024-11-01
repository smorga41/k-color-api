import random
from math import ceil
from typing import List, Tuple, Dict

def generate_graph_nd(N: int, D: float) -> Dict[int, List[int]]:
    """
    Generates a connected graph with N nodes with a density of D
    """
    if D < 0 or D > 1:
        raise ValueError("Graph desnity must be between 0 and 1")
    
    max_edges = (N*(N-1)) / 2
    E = ceil(max_edges * D)

    return generate_graph_ne(N, E)
    

def generate_graph_ne(N: int, E: int) -> Dict[int, List[int]]:
    """
    Generates a connected graph with N nodes and E edges.

    :param N: Number of nodes
    :param E: Number of edges
    :return: Graph represented as an adjacency list
    """
    if E < N - 1:
        raise ValueError("Number of edges must be at least N-1 to form a connected graph.")
    max_edges = N * (N - 1) // 2
    if E > max_edges:
        raise ValueError(f"Number of edges cannot exceed {max_edges} for a simple graph with {N} nodes.")
    
    density = E / max_edges

    nodes, edges = generate_mst(N)
    
    extra_edges = E - (N - 1)
    if density < 0.25:
        # Randomly generate edges until E unique when density low
        for _ in range(extra_edges):
            new_edge = generate_random_edge(edges, N - 1)
            edges.append(new_edge)
    
    else:
        edges = generate_edges_from_set(N, edges, extra_edges)
        
    graph = nodes_edges_to_graph(nodes, edges)
    return graph

def generate_mst(N: int) -> Tuple[List[int], List[Tuple[int, int]]]:
    """
    Generates a random Minimum Spanning Tree (MST) with N nodes.

    :param N: Number of nodes
    :return: A tuple containing the list of nodes and list of edges
    """
    nodes = list(range(N))
    edges: List[Tuple[int, int]] = []
    
    # Shuffle nodes to ensure randomness
    random.shuffle(nodes)
    
    # Connect nodes to form a tree (N-1 edges)
    for i in range(1, N):
        random_prev_node = random.randint(0, i - 1)
        node1 = nodes[i]
        node2 = nodes[random_prev_node]
        edge = tuple(sorted((node1, node2)))
        edges.append(edge)
    
    return nodes, edges

def generate_random_edge(edges: List[Tuple[int, int]], max_node_value: int) -> Tuple[int, int]:
    """
    Generates a random edge until one is found that does not already exist in the list of edges.

    :param edges: Existing list of edges
    :param max_node_value: Maximum node index (assuming nodes are labeled from 0 to max_node_value)
    :return: A unique edge as a tuple (node1, node2)
    """
    existing_edges = set(edges)
    while True:
        node1 = random.randint(0, max_node_value)
        node2 = random.randint(0, max_node_value)
        
        if node1 == node2:
            continue  # Avoid loops
        
        edge = tuple(sorted((node1, node2)))
        
        if edge not in existing_edges:
            return edge

def generate_edges_from_set(N, edges, extra_edges):
    # Sample extra edges from the set of all possible unused edges
    existing_edges = set(edges)
    all_possible_edges = set()
    for i in range(N):
        for j in range(i + 1, N):
            edge = (i, j)
            if edge not in existing_edges:
                all_possible_edges.add(edge)
    if extra_edges > len(all_possible_edges):
        raise ValueError("Not enough unused edges to sample the required number of extra edges.")
    sampled_extra_edges = random.sample(sorted(all_possible_edges), extra_edges)
    edges.extend(sampled_extra_edges)

    return edges

def nodes_edges_to_graph(nodes: List[int], edges: List[Tuple[int, int]]) -> Dict[int, List[int]]:
    """
    Converts lists of nodes and edges into an adjacency list representation of a graph.

    :param nodes: List of node identifiers
    :param edges: List of edges as tuples (node1, node2)
    :return: Graph represented as an adjacency list
    """
    graph: Dict[int, List[int]] = {node: [] for node in nodes}
    
    for node1, node2 in edges:
        graph[node1].append(node2)
        graph[node2].append(node1)
    
    return graph

# Example usage:
if __name__ == "__main__":
    N = 100  # Number of nodes
    E = 1000  # Number of edges
    graph = generate_graph_nd(N, 0.0001)
    print("Adjacency List Representation of the Graph:")
    for node, neighbors in graph.items():
        print(f"{node}: {neighbors}")
