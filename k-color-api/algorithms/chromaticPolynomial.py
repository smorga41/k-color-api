def compute_chromatic_polynomial(adj_list):
    # Check for self-loops
    for node, neighbors in adj_list.items():
        if node in neighbors:
            return [0]
    
    # Base case: no edges
    if all(len(neighbors) == 0 for neighbors in adj_list.values()):
        n = len(adj_list)
        coeffs = [1] + [0] * n
        return coeffs

    # Recursive case
    # Pick an edge (u, v)
    for u, neighbors in adj_list.items():
        if neighbors:
            v = neighbors[0]
            break

    # Edge deletion
    adj_list_deleted = {node: neighbors.copy() for node, neighbors in adj_list.items()}
    # Remove edge (u, v)
    adj_list_deleted[u].remove(v)
    adj_list_deleted[v].remove(u)

    # Edge contraction
    adj_list_contracted = contract_edge(adj_list, u, v)

    # Recursive calls
    coeffs_deleted = compute_chromatic_polynomial(adj_list_deleted)
    coeffs_contracted = compute_chromatic_polynomial(adj_list_contracted)

    # Determine the degree of each polynomial
    degree_contracted = len(coeffs_contracted) - 1
    degree_deleted = len(coeffs_deleted) - 1

    # Determine the maximum degree
    max_degree = max(degree_contracted, degree_deleted)

    # Pad the coefficient lists to align them
    coeffs_contracted = [0] * (max_degree - degree_contracted) + coeffs_contracted
    coeffs_deleted = [0] * (max_degree - degree_deleted) + coeffs_deleted

    # Compute the coefficients for the current graph
    coeffs = [d - c for c, d in zip(coeffs_contracted, coeffs_deleted)]
    return coeffs


def contract_edge(adj_list, u, v):
    # Create a deep copy of the adjacency list without node v
    adj_list_contracted = {node: neighbors.copy() for node, neighbors in adj_list.items() if node != v}

    # Merge v's neighbors into u's adjacency list
    for neighbor in adj_list[v]:
        if neighbor != u:
            adj_list_contracted[u].append(neighbor)
            
    # Remove duplicates and self-loops from u's adjacency list
    adj_list_contracted[u] = list(set(adj_list_contracted[u]))
    if u in adj_list_contracted[u]:
        adj_list_contracted[u].remove(u)
    
    # Replace references to v with u in the graph
    for neighbor in adj_list_contracted:
        adj_list_contracted[neighbor] = [u if x == v else x for x in adj_list_contracted[neighbor]]
        # Remove self-loops if any
        adj_list_contracted[neighbor] = list(set(adj_list_contracted[neighbor]))
        if neighbor in adj_list_contracted[neighbor]:
            adj_list_contracted[neighbor].remove(neighbor)

    return adj_list_contracted

def evaluate_chromatic_polynomial(coefficients, k):
    """
    Evaluates the chromatic polynomial P(G, k) for a given k using Horner's method.

    Parameters:
    - coefficients (list of int/float): Coefficients of the chromatic polynomial,
      ordered from the highest degree term to the constant term.
    - k (int): The number of colors to evaluate the polynomial at.

    Returns:
    - int/float: The value of P(G, k).
    """
    result = 0
    for coef in coefficients:
        result = result * k + coef
    return result

def compute_chromatic_number(coefficients, max_k=None):
    """
    Computes the chromatic number χ(G) from the chromatic polynomial coefficients.

    Parameters:
    - coefficients (list of int/float): Coefficients of the chromatic polynomial,
      ordered from the highest degree term to the constant term.
    - max_k (int, optional): The maximum value of k to evaluate to prevent infinite loops.
      Defaults to the number of coefficients (degree of the polynomial).

    Returns:
    - int: The chromatic number χ(G).
    
    Raises:
    - ValueError: If the chromatic number cannot be determined within the specified range.
    """
    # If max_k is not provided, set it to the degree of the polynomial
    polynomial_evaluation = []

    if max_k is None:
        max_k = len(coefficients)
    
    for k in range(1, max_k + 1):
        Pk = evaluate_chromatic_polynomial(coefficients, k)
        polynomial_evaluation.append(Pk)
        if Pk > 0:
            return k, polynomial_evaluation
    
    raise ValueError(f"Chromatic number could not be determined for k up to {max_k}.")
