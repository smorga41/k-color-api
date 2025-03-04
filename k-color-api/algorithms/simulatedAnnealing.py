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
         cost = α*(# conflicts) + (distinct_colors - 1)
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
                current_solution[node] = random.randint(1, max(1, k0))
    else:
        # No initial assignment provided, so use DSatur to get an initial proper coloring.
        dsatur_result = dsatur_coloring(graph, record_steps=False, initial_assignment=None)
        current_solution = dsatur_result["coloring"]
        # In this case, no nodes are fixed.

    # --- Initialize bookkeeping for conflicts and distinct colors ---
    def full_conflict_count(solution):
        """Compute the total number of conflicting edges (each counted once)."""
        conflicts = 0
        for node, neighbors in graph.items():
            for nbr in neighbors:
                if node < nbr and solution[node] == solution[nbr]:
                    conflicts += 1
        return conflicts

    # Compute initial conflicts using full scan (only done once)
    current_conflicts = full_conflict_count(current_solution)
    # Build a dictionary to track the frequency of each color.
    color_counts = {}
    for color in current_solution.values():
        color_counts[color] = color_counts.get(color, 0) + 1
    current_distinct = len(color_counts)
    
    # Cost function: cost = (n+1)*(# conflicts) + (distinct_colors - 1)
    current_cost = (n + 1) * current_conflicts + (current_distinct - 1)
    best_solution = current_solution.copy()
    best_cost = current_cost

    steps = []  # For recording intermediate steps if requested.
    if record_steps:
        steps.append(current_solution.copy())
    
    # --- SA parameters ---
    max_iter = 10000 * n
    # Set the initial temperature T0 as the initial cost (ensuring it's at least 1).
    T0 = current_cost if current_cost > 0 else 1.0

    # --- Main SA loop ---
    for iteration in range(max_iter):
        # Adaptive temperature: slower cooling schedule
        T = T0 / (1 + iteration / (100 * n))
        
        # Get list of free (non-fixed) nodes.
        free_nodes = list(set(graph.keys()) - fixed_nodes)
        if not free_nodes:
            break  # nothing to change
        
        # Prefer nodes that are in conflict.
        conflict_nodes = [
            node for node in free_nodes 
            if any(current_solution[node] == current_solution[nbr] for nbr in graph[node])
        ]
        if conflict_nodes:
            node = random.choice(conflict_nodes)
        else:
            node = random.choice(free_nodes)
        
        old_color = current_solution[node]
        # Use the maximum color in the current solution as a basis.
        current_max = max(current_solution.values())
        new_color = old_color
        while new_color == old_color:
            new_color = random.randint(1, current_max + 1)
        
        # --- Compute the local change in conflicts ---
        # Only edges incident on 'node' are affected. For each neighbor, check whether the edge
        # (node, neighbor) is counted in our conflict count (using node < neighbor for one ordering
        # and node > neighbor for the other).
        delta_conflicts = 0
        for nbr in graph[node]:
            # Determine if this edge is counted (either as (node, nbr) if node < nbr, or (nbr, node) if nbr < node).
            if node < nbr or node > nbr:
                before = 1 if current_solution[nbr] == old_color else 0
                after  = 1 if current_solution[nbr] == new_color else 0
                delta_conflicts += (after - before)
        candidate_conflicts = current_conflicts + delta_conflicts
        
        # --- Compute the change in distinct colors ---
        # Check if changing node's color removes the only occurrence of old_color
        # and whether new_color is a brand-new color.
        delta_distinct = 0
        if color_counts.get(old_color, 0) == 1:
            delta_distinct -= 1
        if new_color not in color_counts:
            delta_distinct += 1
        candidate_distinct = current_distinct + delta_distinct
        
        # --- Compute candidate cost ---
        candidate_cost = (n + 1) * candidate_conflicts + (candidate_distinct - 1)
        delta_total = candidate_cost - current_cost
        
        # Decide whether to accept the move.
        if delta_total <= 0 or random.random() < math.exp(-delta_total / T):
            # Accept the move.
            current_solution[node] = new_color
            current_conflicts = candidate_conflicts
            current_distinct = candidate_distinct
            current_cost = candidate_cost

            # Update color counts.
            color_counts[old_color] -= 1
            if color_counts[old_color] == 0:
                del color_counts[old_color]
            color_counts[new_color] = color_counts.get(new_color, 0) + 1

            # If this is the best solution so far, record it.
            if current_cost < best_cost:
                best_solution = current_solution.copy()
                best_cost = current_cost

            if record_steps:
                steps.append(current_solution.copy())
        
        # (Optional early stopping: if a proper coloring is found, one might choose to break.)
        if current_conflicts == 0 and iteration % (1000 * n) == 0:
            # Uncomment the following lines if early termination is desired:
            # print("Proper coloring found; terminating early at iteration", iteration)
            # break
            pass

    end_time = time.time()
    
    # Final best solution.
    final_solution = best_solution
    # For reporting, we use the number of distinct colors (which is our improved measure).
    chromatic_number = len(set(final_solution.values()))
    
    # Populate the result object.
    res_obj["chromatic_number"] = chromatic_number
    res_obj["k"] = chromatic_number
    res_obj["runtime (s)"] = end_time - start_time
    res_obj["steps"] = steps if record_steps else []
    res_obj["coloring"] = final_solution.copy()
    
    return res_obj
