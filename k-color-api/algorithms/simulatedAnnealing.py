import time
import random
import math
from collections import defaultdict
from .algorithmResult import algorithmResultTemplate
# (Assuming dsatur_coloring is in the same package if you want to use it to generate a starting solution)
from .dsatur import dsatur_coloring  

def simulated_annealing_coloring(graph, record_steps=False, initial_assignment=None):
    """
    Performs graph coloring using a simulated annealing approach.
    Optionally accepts an initial coloring (a dict mapping node -> color) that will be
    preserved (i.e. fixed) while SA adjusts the remaining nodes.
    
    The returned result is a dict (based on algorithmResultTemplate) with keys:
       "chromatic_number", "k", "runtime (s)", "steps", "coloring"
       
    The algorithm minimizes a cost function:
         cost = α * (# conflicts) + (max(color) - 1)
    where α is chosen as (n + 1) to strongly penalize any conflict over color count.
    """
    # Copy the template so we don't overwrite the original
    res_obj = algorithmResultTemplate.copy()
    
    start_time = time.time()
    n = len(graph)
    
    # Check for self-loops (which make proper coloring impossible)
    for node, neighbors in graph.items():
        if node in neighbors:
            # Self-loop detected: no proper coloring possible
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

    # Determine the set of nodes that should remain fixed
    fixed_nodes = set(initial_assignment.keys()) if initial_assignment is not None else set()
    
    # --- Initialize the solution ---
    # If an initial assignment is provided, use it for those nodes and randomly assign colors for the others.
    # Otherwise, we use DSatur to get an initial proper coloring.
    current_solution = {}
    if initial_assignment is not None:
        # Use the given colors for fixed nodes.
        # For unfixed nodes, assign a random color in [1, k0],
        # where we set k0 = max(initial_assignment) if available, or 1.
        if initial_assignment:
            k0 = max(initial_assignment.values())
        else:
            k0 = 1
        for node in graph:
            if node in fixed_nodes:
                current_solution[node] = initial_assignment[node]
            else:
                # Random assignment from 1 to k0 (if k0 is 0, default to 1)
                current_solution[node] = random.randint(1, max(1, k0))
    else:
        # No initial assignment provided, so use DSatur to get an initial proper coloring.
        dsatur_result = dsatur_coloring(graph, record_steps=False, initial_assignment=None)
        current_solution = dsatur_result["coloring"]
        # In this case, no nodes are fixed.
    
    # --- Define helper functions ---
    def count_conflicts(solution):
        """
        Count the number of conflicting edges in the current coloring.
        Each edge is counted only once.
        """
        conflicts = 0
        for node, neighbors in graph.items():
            for nbr in neighbors:
                # Ensure each edge is counted only once.
                if node < nbr and solution[node] == solution[nbr]:
                    conflicts += 1
        return conflicts

    def cost(solution):
        """
        Compute the cost of a solution.
        cost = α*(# conflicts) + (max(color) - 1)
        We set α = n + 1.
        """
        conflicts = count_conflicts(solution)
        max_color = max(solution.values()) if solution else 1
        return (n + 1) * conflicts + (max_color - 1)
    
    current_cost = cost(current_solution)
    best_solution = current_solution.copy()
    best_cost = current_cost

    steps = []  # For recording intermediate steps if requested.
    if record_steps:
        steps.append(current_solution.copy())
    
    # --- SA parameters ---
    # Maximum number of iterations; you can adjust this based on graph size.
    max_iter = 10000 * n
    # Initial temperature. (One common choice is to start proportional to the initial cost.)
    T = current_cost if current_cost > 0 else 1.0
    # Cooling rate (multiplicative factor per iteration)
    cooling_rate = 0.995

    # --- Main SA loop ---
    for iteration in range(max_iter):
        # Get list of nodes that are not fixed.
        free_nodes = list(set(graph.keys()) - fixed_nodes)
        if not free_nodes:
            break  # nothing to change
        
        # Choose a random (free) vertex
        node = random.choice(free_nodes)
        old_color = current_solution[node]
        current_max = max(current_solution.values())
        # Propose a new color: choose uniformly from 1 to current_max+1.
        # (Allowing a new color can help break conflicts but will increase cost if not necessary.)
        new_color = old_color
        while new_color == old_color:
            new_color = random.randint(1, current_max + 1)
        
        # Create a candidate solution by changing the color of the chosen node.
        candidate = current_solution.copy()
        candidate[node] = new_color
        candidate_cost = cost(candidate)
        delta = candidate_cost - current_cost
        
        # Decide whether to accept the move.
        if delta <= 0 or random.random() < math.exp(-delta / T):
            current_solution = candidate
            current_cost = candidate_cost
            # If this candidate is the best seen so far, record it.
            if current_cost < best_cost:
                best_solution = current_solution.copy()
                best_cost = current_cost
            if record_steps:
                steps.append(current_solution.copy())
        
        # Decrease temperature gradually.
        T *= cooling_rate

        # (Optional) If a proper coloring is found (i.e. 0 conflicts) and no improvements have been seen for a while,
        # you might choose to break out of the loop.
        if count_conflicts(best_solution) == 0 and iteration % (1000 * n) == 0:
            # For example, after every 1000*n iterations, if we already have a proper coloring, you may break early.
            # (Comment out the following two lines if you want the full run.)
            # print("Proper coloring found; terminating early at iteration", iteration)
            # break
            pass

    end_time = time.time()
    
    # Final best solution:
    final_solution = best_solution
    # For reporting, we assume the chromatic number is the highest color used.
    chromatic_number = max(final_solution.values())
    
    # Populate result object.
    res_obj["chromatic_number"] = chromatic_number
    res_obj["k"] = chromatic_number
    res_obj["runtime (s)"] = end_time - start_time
    res_obj["steps"] = steps if record_steps else []
    res_obj["coloring"] = final_solution.copy()
    
    return res_obj
