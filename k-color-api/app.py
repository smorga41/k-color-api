from flask import Flask, jsonify, request
from flask_cors import CORS
import traceback

from database.db_manager import MongoDBManager
from algorithms.greedy import greedy_coloring, greedy_bfs_coloring
from algorithms.backtrack import find_min_k_backtracking
from algorithms.chromaticPolynomial import compute_chromatic_polynomial

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

    valid_algorithms = {
        "greedy": greedy_coloring,
        "greedy_bfs": greedy_bfs_coloring,
        "backtrack": find_min_k_backtracking,
        "deletion_contraction": compute_chromatic_polynomial
    }

    try:
        coloring_result = valid_algorithms[algorithm_name](graph)
    except Exception as e:
        return jsonify({
            'message': f'Error occured while executing the {algorithm_name} algorithm: {str(e)} \n {traceback.format_exc()}'
        }), 500
    
    return jsonify({
        'result': coloring_result
    }), 200

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
        graph_id = db_manager.save_graph(data)  # Assuming 'save_graph' returns the inserted ID
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
