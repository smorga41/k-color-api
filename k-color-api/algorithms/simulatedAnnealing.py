import time
import random
import math
from .algorithmResult import algorithmResultTemplate
from .dsatur import dsatur_coloring  
from .greedy import greedy_coloring, greedy_bfs_coloring

def simulated_annealing_coloring(graph, record_steps=False):
    """
    Performs graph coloring using a simulated annealing approach.
    Returns a dict (based on algorithmResultTemplate) with keys:
       "chromatic_number", "k", "runtime (s)", "steps", "coloring"
       
    The algorithm minimizes a cost function:
         cost = (n+1) * (# conflicts) + (distinct_colors - 1)
    """
    res_obj = algorithmResultTemplate.copy()
    start_time = time.time()
    n = len(graph)
    
    # Check for self-loops (which make proper coloring impossible)
    for node, neighbors in graph.items():
        if node in neighbors:
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
    
    # --- Initialize the solution using a greedy approach ---
    greedy_result = greedy_coloring(graph, record_steps=False)
    current_solution = greedy_result["coloring"]
    
    # --- Initialize conflict count and color bookkeeping ---
    def full_conflict_count(solution):
        """Count each conflict edge only once."""
        conflicts = 0
        for node, neighbors in graph.items():
            for nbr in neighbors:
                if node < nbr and solution[node] == solution[nbr]:
                    conflicts += 1
        return conflicts
    
    current_conflicts = full_conflict_count(current_solution)
    color_counts = {}
    for color in current_solution.values():
        color_counts[color] = color_counts.get(color, 0) + 1
    current_distinct = len(color_counts)
    current_cost = (n + 1) * current_conflicts + (current_distinct - 1)
    best_solution = current_solution.copy()
    best_cost = current_cost
    
    steps = []
    if record_steps:
        steps.append(current_solution.copy())
    
    # --- SA parameters ---
    max_iter = 1000 * n  # Reduced total iterations.
    T0 = current_cost if current_cost > 0 else 1.0
    no_improvement_counter = 0  # For adaptive stopping.
    
    for iteration in range(max_iter):
        # Adaptive temperature: slower cooling.
        T = T0 / (1 + iteration / (100 * n))
        
        # Select a node that is in conflict, if any.
        conflict_nodes = [node for node in graph 
                          if any(current_solution[node] == current_solution[nbr] for nbr in graph[node])]
        if conflict_nodes:
            node = random.choice(conflict_nodes)
        
        old_color = current_solution[node]
        current_max = max(current_solution.values())
        new_color = old_color
        # Randomly choose a different color (possibly introducing a new color)
        while new_color == old_color:
            new_color = random.randint(1, current_max + 1)
        
        # --- Compute local change in conflicts ---
        # Instead of an explicit loop, use generator expressions (runs in C speed).
        conflict_before = sum(1 for nbr in graph[node] if current_solution.get(nbr) == old_color)
        conflict_after = sum(1 for nbr in graph[node] if current_solution.get(nbr) == new_color)
        delta_conflicts = conflict_after - conflict_before
        candidate_conflicts = current_conflicts + delta_conflicts
        
        # --- Compute change in distinct colors ---
        delta_distinct = 0
        if color_counts.get(old_color, 0) == 1:
            delta_distinct -= 1
        if new_color not in color_counts:
            delta_distinct += 1
        candidate_distinct = current_distinct + delta_distinct
        
        candidate_cost = (n + 1) * candidate_conflicts + (candidate_distinct - 1)
        delta_total = candidate_cost - current_cost
        
        # --- Acceptance criterion ---
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
            
            # Update best solution if improved.
            if current_cost < best_cost:
                best_solution = current_solution.copy()
                print(iteration, "new best", current_cost)
                best_cost = current_cost
                no_improvement_counter = 0
            else:
                no_improvement_counter += 1
            
            if record_steps:
                steps.append(current_solution.copy())
        else:
            no_improvement_counter += 1
        
        # --- Adaptive stopping condition ---
        if no_improvement_counter > 5000:
            print("early halt")
            break
        
    print("end reached", iteration, max_iter)
    end_time = time.time()
    final_solution = best_solution
    chromatic_number = len(set(final_solution.values()))
    
    res_obj["chromatic_number"] = chromatic_number
    res_obj["k"] = chromatic_number
    res_obj["runtime (s)"] = end_time - start_time
    res_obj["steps"] = steps if record_steps else []
    res_obj["coloring"] = final_solution.copy()
    
    return res_obj
