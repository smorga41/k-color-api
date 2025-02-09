import random
import string
from time import time
from typing import List, Tuple, Dict

from utils.utils import ND_to_NE, DE_to_NE

def generate_random_graph(N, D, E, db_manager):
    #TODO add validation that exactly 2 of N,D,E are present and the third is None
    if not D:
        return generate_graph_ne(N, E, db_manager)
    elif not E:
        return generate_graph_nd(N, D, db_manager)
    elif not N:
        return generate_graph_de(D, E, db_manager)
    

def generate_graph_de(D: float, E: int, db_manager):
    N, E = DE_to_NE(D, E)

    return generate_graph_ne(N, E, db_manager)

def generate_graph_nd(N: int, D: float, db_manager) -> Dict[int, List[int]]:
    """
    Generates a connected undirected graph with N nodes and density D.
    """
    N, E = ND_to_NE(N, D)
    # if D <= 0 or D >= 1:
    #     raise ValueError("Graph density must be between 0 and 1 (non-inclusive).")
    
    # max_edges = N * (N - 1) // 2
    # E = int(max_edges * D)
    # if E < N - 1:
    #     E = N - 1  # Ensure the graph can be connected
    return generate_graph_ne(N, E, db_manager)

def generate_graph_ne(N: int, E: int, db_manager) -> Dict[int, List[int]]:
    """
    Generates a connected undirected graph with N nodes and E edges.
    """
    if E < N - 1:
        raise ValueError("Number of edges must be at least N-1 to form a connected graph.")
    max_edges = N * (N - 1) // 2
    if E > max_edges:
        raise ValueError(f"Number of edges cannot exceed {max_edges} for a simple graph with {N} nodes.")
    
    # Generate a random Minimum Spanning Tree (MST)
    nodes, edges = generate_mst(N)
    edges_set = set(edges)

    K = E - (N - 1)  # Number of extra edges needed

    while len(edges_set) < E:
        remaining_edges = E - len(edges_set)
        num_to_generate = remaining_edges * 2  # Generate extra to account for duplicates and existing edges
        i_nodes = random.choices(range(N), k=num_to_generate)
        j_nodes = random.choices(range(N), k=num_to_generate)

        # Remove self-loops and create edges
        new_edges = set()
        for i, j in zip(i_nodes, j_nodes):
            if i == j:
                continue  # Skip self-loops
            edge = tuple(sorted((str(i), str(j))))
            if edge not in edges_set:
                new_edges.add(edge)
                if len(new_edges) + len(edges_set) >= E:
                    break  # Stop if we've reached the desired number of edges

        edges_set.update(new_edges)

    edges = list(edges_set)
    graph = nodes_edges_to_graph(nodes, edges)
    saved_id = storeGraphinMongo(graph, "random", N, E, db_manager)
    return {"_id": saved_id, "graph": graph, "chromatic_number": None, "Description": f"A randomly generated graph with {N} nodes and {E} edges"}

def generate_mst(N: int) -> Tuple[List[int], List[Tuple[int, int]]]:
    """
    Generates a random Minimum Spanning Tree (MST) with N nodes.
    """
    nodes = list(range(N))
    edges: List[Tuple[int, int]] = []
    parent = list(range(N))
    random.shuffle(nodes)

    # Connect nodes to form a tree (N-1 edges)
    for i in range(1, N):
        node1 = str(nodes[i])
        node2 = str(nodes[random.randint(0, i - 1)])
        edge = tuple(sorted((node1, node2)))
        edges.append(edge)

    return nodes, edges

def nodes_edges_to_graph(nodes: List[int], edges: List[Tuple[int, int]]) -> Dict[int, List[int]]:
    """
    Converts lists of nodes and edges into an adjacency list representation of a graph.
    """
    graph: Dict[str, List[str]] = {str(node): [] for node in nodes}
    for node1, node2 in edges:
        graph[node1].append(node2)
        graph[node2].append(node1)
    return graph

def storeGraphinMongo(graph, graph_type, N, E, db_manager, custom=False, name=None):
    if not name:
        name = [graph_type, str(N), str(E), str(''.join(random.choices(string.ascii_uppercase + string.digits, k=10)))]
        name = "_".join(name)
    graph_data = {
        "name": name,
        "description": None,
        "format": "adjacency_list",
        "custom": custom,
        "graph_type": graph_type,
        "N": N,
        "E": E,
        "chromatic_number": None,
        "graph": graph
    }

    saved_id = db_manager.save_graph(graph_data)
    return saved_id
    

