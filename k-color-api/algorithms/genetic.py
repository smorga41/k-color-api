import time
import random
import math
from .algorithmResult import algorithmResultTemplate
from .dsatur import dsatur_coloring  # for seeding initial solutions
from .greedy import greedy_coloring  # for seeding initial solutions
from .metropolis import metropolis_coloring  # for seeding initial solutions

def genetic_coloring(
    graph,
    record_steps=False,
    q=None,
    population_size=50,
    max_generations=100,
    crossover_rate=0.8,
    mutation_rate=0.05,
):
    """
    Improved Genetic Algorithm for graph coloring with elitism and memetic local search.
    
    This implementation incorporates:
      - A cost function that penalizes both conflicts and high color count.
      - Informed crossover and mutation operators.
      - Seeding of the initial population.
      - A local search (hill-climbing) step on offspring that uses incremental evaluation.
      - Elitism to preserve the best individual across generations.
      
    Returns a dictionary with keys:
       "k", "runtime (s)", "steps", "coloring", "chromatic_number"
    """
    if not q:
        q = choose_q(graph)

    res_obj = algorithmResultTemplate.copy()
    start_time = time.time()
    n = len(graph)

    if not graph:
        end_time = time.time()
        res_obj["k"] = 0
        res_obj["runtime (s)"] = end_time - start_time
        res_obj["steps"] = []
        res_obj["coloring"] = {}
        res_obj["chromatic_number"] = None
        return res_obj

    # --- Fitness & Cost Functions ---
    def compute_conflicts(coloring):
        """Count conflicting edges (each counted once)."""
        conflicts = 0
        for v, neighbors in graph.items():
            for nbr in neighbors:
                if nbr > v and coloring[v] == coloring[nbr]:
                    conflicts += 1
        return conflicts

    def distinct_colors(coloring):
        """Return the number of distinct colors used."""
        return len(set(coloring.values()))

    def cost(coloring):
        """Cost = (n+1)*conflicts + (distinct_colors - 1). Lower is better."""
        c = compute_conflicts(coloring)
        d = distinct_colors(coloring)
        return (n + 1) * c + (d - 1)

    def fitness(coloring):
        """Higher fitness for lower cost."""
        return 1.0 / (1.0 + cost(coloring))

    # --- Incremental Evaluation Helper ---
    def compute_node_conflicts(node, coloring):
        """
        Compute the number of conflicts for a single node by comparing its color
        against those of its neighbors.
        """
        return sum(1 for nbr in graph[node] if coloring.get(nbr) == coloring[node])

    # --- Local Search (Memetic) Step Using Incremental Evaluation ---
    def local_search(individual, max_iter=5):
        """
        Perform a hill-climbing search on the individual.
        For each node, try alternative colors using only a local (incremental) evaluation.
        """
        improved = True
        iter_count = 0
        while improved and iter_count < max_iter:
            improved = False
            for node in individual.keys():
                current_color = individual[node]
                current_local = compute_node_conflicts(node, individual)
                best_color = current_color
                # Try all possible colors from 1 to q.
                for color in range(1, q + 1):
                    if color == current_color:
                        continue
                    individual[node] = color
                    new_local = compute_node_conflicts(node, individual)
                    if new_local < current_local:
                        best_color = color
                        current_local = new_local
                        improved = True
                    # Restore original color for the next candidate.
                    individual[node] = current_color
                individual[node] = best_color
            iter_count += 1
        return individual

    # --- Seed Initial Population ---
    population = []
    # Use a fraction of the individuals from a greedy heuristic.
    heuristic_count = max(1, int(0.2 * population_size))
    try:
        heuristic_solution = greedy_coloring(graph, record_steps=False, initial_assignment=None)["coloring"]
    except Exception:
        heuristic_solution = None

    if heuristic_solution is not None:
        population.append(heuristic_solution.copy())
        for _ in range(heuristic_count - 1):
            sol = heuristic_solution.copy()
            # Introduce slight perturbations.
            for node in sol:
                if random.random() < 0.1:
                    sol[node] = random.randint(1, q)
            population.append(sol)
    # Fill remaining individuals with random colorings.
    while len(population) < population_size:
        individual = {node: random.randint(1, q) for node in graph}
        population.append(individual)

    # --- Selection Operator ---
    def tournament_selection(pop, k=3):
        selected = random.sample(pop, k)
        best = max(selected, key=lambda ind: fitness(ind))
        return best

    # --- Informed Crossover Operator ---
    def informed_crossover(parent1, parent2):
        """
        For each node:
          - If both parents agree, use that color.
          - Otherwise, compute local conflict counts and choose the color from the parent
            with the lower conflict count (or pick randomly if equal).
        """
        child = {}
        for node in graph:
            if parent1[node] == parent2[node]:
                child[node] = parent1[node]
            else:
                def local_conflicts(parent, node):
                    return sum(1 for nbr in graph[node] if parent[nbr] == parent[node])
                lc1 = local_conflicts(parent1, node)
                lc2 = local_conflicts(parent2, node)
                if lc1 < lc2:
                    child[node] = parent1[node]
                elif lc2 < lc1:
                    child[node] = parent2[node]
                else:
                    child[node] = random.choice([parent1[node], parent2[node]])
        return child

    def crossover(parent1, parent2):
        if random.random() > crossover_rate:
            return parent1.copy(), parent2.copy()
        child1 = informed_crossover(parent1, parent2)
        child2 = informed_crossover(parent2, parent1)
        return child1, child2

    # --- Informed Mutation Operator with Incremental Evaluation ---
    def mutate(individual):
        """
        For each node in conflict, with probability mutation_rate,
        try alternative colors using only a local evaluation of conflicts.
        """
        for node in list(individual.keys()):
            # Only consider nodes that are currently in conflict.
            if any(individual[node] == individual.get(nbr) for nbr in graph[node]):
                if random.random() < mutation_rate:
                    current_color = individual[node]
                    current_local = compute_node_conflicts(node, individual)
                    best_color = current_color
                    # Consider candidate colors from the neighborhood plus one random color.
                    candidate_colors = set(individual[nbr] for nbr in graph[node])
                    candidate_colors.add(current_color)
                    candidate_colors.add(random.randint(1, q))
                    for color in candidate_colors:
                        if color == current_color:
                            continue
                        individual[node] = color
                        new_local = compute_node_conflicts(node, individual)
                        if new_local < current_local:
                            best_color = color
                            current_local = new_local
                    individual[node] = best_color
        return individual

    # --- Main GA Loop ---
    steps = []
    best_individual = None
    best_cost_val = math.inf

    for generation in range(max_generations):
        # Evaluate current population.
        for ind in population:
            current_cost_val = cost(ind)
            if current_cost_val < best_cost_val:
                best_cost_val = current_cost_val
                best_individual = ind.copy()

        if record_steps:
            steps.append(best_individual.copy())

        new_population = []
        # Elitism: carry the best individual forward.
        elite = best_individual.copy()

        while len(new_population) < population_size:
            parent1 = tournament_selection(population)
            parent2 = tournament_selection(population)
            child1, child2 = crossover(parent1, parent2)
            mutate(child1)
            mutate(child2)
            # Apply local search (memetic improvement) to each child.
            child1 = local_search(child1, max_iter=5)
            child2 = local_search(child2, max_iter=5)
            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)

        # Replace the worst individual with the elite if it improves the cost.
        worst = max(new_population, key=lambda ind: cost(ind))
        if cost(elite) < cost(worst):
            new_population[new_population.index(worst)] = elite

        population = new_population

    end_time = time.time()
    used_colors = set(best_individual.values())
    k_used = len(used_colors)

    res_obj["k"] = k_used
    res_obj["runtime (s)"] = end_time - start_time
    res_obj["steps"] = steps if record_steps else []
    res_obj["coloring"] = best_individual
    # The GA does not guarantee the optimal chromatic number.
    res_obj["chromatic_number"] = None

    return res_obj

def choose_q(graph):
    return max(len(neighbors) for neighbors in graph.values()) + 1
