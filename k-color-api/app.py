from flask import Flask, jsonify, request
from flask_cors import CORS
import traceback

from database.db_manager import MongoDBManager
from algorithms.greedy import greedy_coloring, greedy_bfs_coloring
from algorithms.dsatur import dsatur_coloring
from algorithms.recursiveLargestFirst import rlf_coloring
from algorithms.backtrack import find_min_k_backtracking
from algorithms.chromaticPolynomial import compute_chromatic_polynomial, compute_chromatic_number
from algorithms.metropolis import metropolis_coloring
from algorithms.genetic import genetic_coloring
from algorithms.simulatedAnnealing import simulated_annealing_coloring

from analysis.analyse import run_coloring_experiment
from analysis.scaling import analyse_algorithm_scalability
from utils.validation import validate_graph, validate_algorithm_name, valid_algorithms
from utils.format_results import combine_scaling_result
from utils.get_graph import get_graphs_from_definitions

app = Flask(__name__)
db_manager = MongoDBManager()
CORS(app)

@app.route('/hello-world')
def get_hello_world():
    return jsonify({"message": "Hello world"})

@app.route('/color-graph/', methods=['POST'])
def color_graph():
    data = request.get_json()
    graph = data.get('graph')
    algorithm_name = data.get('algorithm', 'greedy')
    
    # validation
    if validate_graph(graph) is not True:
        return validate_graph(graph)
    
    if validate_algorithm_name(algorithm_name) is not True:
        return validate_algorithm_name(algorithm_name)

    valid_algorithms = valid_algorithms()

    try:
        coloring_result = valid_algorithms[algorithm_name](graph)
    except Exception as e:
        return jsonify({
            'message': f'Error occured while executing the {algorithm_name} algorithm: {str(e)} \n {traceback.format_exc()}'
        }), 500
    
    return jsonify({
        'result': coloring_result
    }), 200

@app.route('/color-graph-config/', methods=['POST'])
def color_graph_from_config():
    data = request.get_json()
    algorithm_name = data.get('algorithm', 'greedy')
    graph_config = data.get('graphConfig', {})

    # Validate the incoming algorithm name (similar to validate_algorithm_name)
    valid_algos = valid_algorithms()
    if algorithm_name not in valid_algos:
        return jsonify({'message': f'Invalid algorithm: {algorithm_name}'}), 400

    try:
        # Generate/retrieve the graph from the single config
        generated_graph = get_graphs_from_definitions([graph_config], db_manager)
        if not generated_graph:
            return jsonify({
                'message': 'No graph could be generated from the provided config.'
            }), 400

        # We only expect a single graph from the single config
        graph = generated_graph[0]['graph']

        # Run the chosen algorithm on that graph
        coloring_result = valid_algos[algorithm_name](graph, True)
        # add extra infromation to result
        chromatic_number = None
        if "chromatic_number" in generated_graph[0].keys():
            chromatic_number = generated_graph[0]['chromatic_number']
        
        description = ""
        if "description" in generated_graph[0].keys():
            description = generated_graph[0]['description']
        
        coloring_result.update({"chromatic_number": chromatic_number})
        coloring_result.update({"graph_description": description})

    except Exception as e:
        return jsonify({
            'message': f'Error occurred while generating or coloring the graph: {str(e)}\n{traceback.format_exc()}'
        }), 500

    return jsonify({'result': coloring_result, 
                    'graph': graph}), 200

@app.route('/get-chromatic-polynomial', methods=['POST'])
def get_chromatic_polynomial():
    data = request.get_json()
    graph_config = data.get('graphConfig', {})

    # Validate the incoming algorithm name (similar to validate_algorithm_name)

    try:
        # Generate/retrieve the graph from the single config
        generated_graphs = get_graphs_from_definitions([graph_config], db_manager)
        # print("generated Graphs", generated_graphs)
        if not generated_graphs:
            return jsonify({
                'message': 'No graph could be generated from the provided config.'
            }), 400

        # We only expect a single graph from the single config
        graph = generated_graphs[0]

        # compute graph stats

        # Run the chosen algorithm on that graph
        chromatic_polynomial = compute_chromatic_polynomial(graph['graph'])
        chromatic_number, polynomial_evaluation = compute_chromatic_number(chromatic_polynomial)

        # update chromatic number in database
        db_manager.upsert_field(graph['_id'], "chromatic_number", chromatic_number)



    except Exception as e:
        return jsonify({
            'message': f'Error occurred while generating or coloring the graph: {str(e)}\n{traceback.format_exc()}'
        }), 500

    return jsonify({'chromatic_polynomial': chromatic_polynomial,
                    'chromatic_polynomial_evaluation': polynomial_evaluation,  
                    'chromatic_number': chromatic_number,
                    'graph': graph['graph']}), 200

@app.route('/analysis', methods=['POST'])
def general_analysis():
    """
    1 graph per graph definition, with the experiment ran <repeats> number of times on the same graph
    """
    data = request.get_json()
    algorithm_names = data.get("algorithms")
    repeats = int(data.get("repeats"))
    graph_definitions = data.get("graphs")

    for algorithm_name in algorithm_names:
        if validate_algorithm_name(algorithm_name) is not True:
            return jsonify({
                'message': validate_algorithm_name(algorithm_name)
            }), 500
    if repeats < 1:
        return jsonify({
            'message': f'Repeats {repeats} is invalid. Must be greater than 1'
        })

    #TODO Validate that each graph to be generated has exactly 2 out of 3 fields filled in 

    # Generate Graphs
    graphs = get_graphs_from_definitions(graph_definitions, db_manager)

    # Run experiement
    try:
        result = run_coloring_experiment(graphs, algorithm_names, repeats)
        return result
    except Exception as e:
        return jsonify({
            'message': f'Error occured while performing general analysis: {e} \n{traceback.format_exc()}'
        }), 500




@app.route('/analysis/scalability', methods=['POST'])
def analyse_scalability():
    data = request.get_json()
    algorithm_names = data.get('algorithms')
    density = data.get('density')
    repeats = data.get('repeats')
    node_sizes = data.get('node_sizes')
    
    if density < 0  or density > 1:
        return jsonify({'message': 'Density must be a value between 0 and 1'})

    for algorithm_name in algorithm_names:
        if validate_algorithm_name(algorithm_name) is not True:
            return jsonify({
                'message': validate_algorithm_name(algorithm_name)
            }), 500
    # Run Experiment

    algorithms = valid_algorithms()
    try:
        experiment_result = {}
        for algorithm_name in algorithm_names:
            algorithm = algorithms[algorithm_name]
            experiment_result.update({algorithm_name: analyse_algorithm_scalability(algorithm, density, node_sizes, repeats, db_manager)})
            result = combine_scaling_result(experiment_result)
        return result
    except Exception as e:
        return jsonify({
            'message': f'Error occured while executing the {algorithm_name} algorithm: {str(e)} \n {traceback.format_exc()}'
        }), 500
    

@app.route('/solve-sudoku', methods=['POST'])
def solve_sudoku():
    """
    Expected JSON payload:
    {
      "puzzle": "050703060007000800000816000000030000005000100730040086906000204840572093000409000",
      "algorithm": "backtrack"  // or "greedy", "dsatur", etc.
    }
    In the puzzle string, use '0' to denote empty cells.
    """
    data = request.get_json()
    puzzle_str = data.get('puzzle')
    algorithm_name = data.get('algorithm', 'backtrack')  # default algorithm

    # Validate the puzzle format
    if not puzzle_str or len(puzzle_str) != 81:
        return jsonify({"message": "Invalid puzzle. Must be exactly 81 characters long."}), 400

    # Convert the puzzle string into a 9x9 board (list of lists) of integers.
    board = []
    for i in range(9):
        row = []
        for j in range(9):
            ch = puzzle_str[i * 9 + j]
            if ch == '0' or ch == '.':
                row.append(0)
            elif ch.isdigit():
                row.append(int(ch))
            else:
                return jsonify({"message": "Invalid character in puzzle. Use digits or 0/."}), 400
        board.append(row)

    # Construct the Sudoku graph.
    # Each cell is a node with id "r{i}c{j}".
    # There is an edge between two nodes if they are in the same row, column, or 3x3 block.
    sudoku_graph = {}
    for i in range(9):
        for j in range(9):
            node_id = f"r{i}c{j}"
            sudoku_graph[node_id] = set()

    for i in range(9):
        for j in range(9):
            node_id = f"r{i}c{j}"
            # Row: all cells in row i (except itself)
            for j2 in range(9):
                if j2 != j:
                    sudoku_graph[node_id].add(f"r{i}c{j2}")
            # Column: all cells in column j (except itself)
            for i2 in range(9):
                if i2 != i:
                    sudoku_graph[node_id].add(f"r{i2}c{j}")
            # Block: cells in the same 3x3 sub-grid.
            bi = (i // 3) * 3
            bj = (j // 3) * 3
            for di in range(3):
                for dj in range(3):
                    ni = bi + di
                    nj = bj + dj
                    if ni == i and nj == j:
                        continue
                    sudoku_graph[node_id].add(f"r{ni}c{nj}")

    # Convert each set to a list for JSON serialization.
    for key in sudoku_graph:
        sudoku_graph[key] = list(sudoku_graph[key])

    # Build the initial assignment from the pre-filled cells.
    # We use a 0-indexed color scheme (i.e. digit 1 is color 0, digit 9 is color 8).
    initial_assignment = {}
    for i in range(9):
        for j in range(9):
            if board[i][j] != 0:
                initial_assignment[f"r{i}c{j}"] = board[i][j]

    # Define the valid sudoku algorithms (reuse your graph coloring algorithms).
    valid_sudoku_algorithms = valid_algorithms()

    if algorithm_name not in valid_sudoku_algorithms:
        return jsonify({"message": f"Invalid algorithm: {algorithm_name}"}), 400

    try:
        solve_algorithm = valid_sudoku_algorithms[algorithm_name]
        # Call the selected algorithm.
        # (Assuming the algorithm functions can accept an initial assignment as a second argument.
        # If not, you might need to modify them to enforce pre-assigned values.)
        coloring_result = solve_algorithm(sudoku_graph, initial_assignment=initial_assignment, record_steps = True)
    except Exception as e:
        return jsonify({
            "message": f"Error occurred while solving Sudoku: {str(e)}\n{traceback.format_exc()}"
        }), 500

    # Expect the coloring_result to include a "steps" array,
    # where the first (or only) element is a mapping { cell_id: color_index, ... }.
    final_assignment = coloring_result.get("steps", [{}])[0]

    # Build the solved Sudoku board from the final assignment.
    solved_board = [[0 for _ in range(9)] for _ in range(9)]
    for i in range(9):
        for j in range(9):
            cell_id = f"r{i}c{j}"
            if cell_id in final_assignment:
                solved_board[i][j] = final_assignment[cell_id] + 1
            else:
                solved_board[i][j] = board[i][j]

    # Package the result.
    result = {
        "solution": solved_board,
        "chromatic_number": coloring_result.get("chromatic_number", 9),
        "steps": coloring_result.get("steps", [final_assignment]),
        "k": coloring_result.get("k", 9),
        "algorithm": algorithm_name
    }

    return jsonify({"result": result, "graph": sudoku_graph}), 200

@app.route("/graphs/get_custom", methods=["GET"])
def get_custom_graphs():
    """
    GET /graphs/get_custom?search=<searchTerm>&page=<pageNum>&limit=<pageSize>
    
    Returns JSON with fields: 
      - results: array of {id, name}
      - total: total number of matching docs
      - hasMore: whether there is another page
    """
    # Get query params (with defaults)
    search = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    try:
        data = db_manager.get_custom_graphs(search, page, limit)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({
            'error': f'Could not retrieve custom graphs: {str(e)}'
        }), 500
    

@app.route("/graphs/upload", methods=["POST"])
def upload_graph():
    data = request.get_json()



    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Validate 'name'
    name = data.get('name')
    if not name or not isinstance(name, str) or not name.strip():
        return jsonify({'error': "'name' is required and must be a non-empty string."}), 400

    # Validate 'graph'
    graph = data.get('graph')
    if not graph or not isinstance(graph, dict):
        return jsonify({'error': "'graph' is required and must be an object containing 'vertices' and 'edges'."}), 400

    chromaticValue = data.get("chromatic_value")
    if  chromaticValue and not isinstance(chromaticValue, int):
        return jsonify({'error': "chromatic value must be an integer"})

    try:
        # Save the graph to MongoDB
        graph_id = db_manager.save_graph(data)
        return jsonify({
            'message': 'Graph uploaded successfully.',
            'id': str(graph_id)
        }), 201
    except Exception as e:
        return jsonify({
            'error': f"An error occurred while saving the graph: {str(e)}"
        }), 500






if __name__ == '__main__':
    app.run(debug=True)
