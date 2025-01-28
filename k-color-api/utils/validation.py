from flask import jsonify

from algorithms.greedy import greedy_coloring, greedy_bfs_coloring
from algorithms.dsatur import dsatur_coloring
from algorithms.recursiveLargestFirst import rlf_coloring
from algorithms.backtrack import find_min_k_backtracking
from algorithms.chromaticPolynomial import compute_chromatic_polynomial

def valid_algorithms():
    return ({
        "greedy": greedy_coloring,
        "greedy_bfs": greedy_bfs_coloring,
        "dsatur": dsatur_coloring,
        "rlf": rlf_coloring,
        "backtrack": find_min_k_backtracking,
        "deletion_contraction": compute_chromatic_polynomial
    })

def validate_graph(graph):

    # Ensure graph exists
    if graph is None:
        return jsonify({"message": "Graph must be provided"}), 400
    
    # Ensure graph is a dictionary
    if not isinstance(graph, dict):
        return jsonify({"message" "Graph must be a dictionary"}), 400
    
    # Ensure graph is represented as an adjacency list
    for node, neighbours in graph.items():
        if not isinstance(neighbours, list):
            return jsonify({'message': f'neighbours of node {node} must be a list'}), 400
    
    return True

def validate_algorithm_name(algorithm_name):
    algorithms = valid_algorithms()
    if algorithm_name not in algorithms.keys():
        return (f'Invalid algorithm {algorithm_name}, Valid options are {', '.join(algorithms.keys())}')

    return True

