from flask import Flask, jsonify, request
from flask_cors import CORS
from algorithms.greedy import greedy_coloring, greedy_bfs_coloring
from algorithms.backtrack import find_min_k_backtracking
from analysis.scaling import analyse_algorithm_scalability
from utils.validation import validate_graph, validate_algorithm_name, valid_algorithms

app = Flask(__name__)
CORS(app)

@app.route('/hello-world')
def get_hello_world():
    return jsonify({"message": "Hello world"})

@app.route('/color-graph/', methods=['POST'])
def color_graph():
    data = request.get_json()
    graph = data.get('graph')
    algorithm = data.get('algorithm', 'greedy')
    
    # validation
    if validate_graph(graph) is not True:
        return validate_graph(graph)
    
    if validate_algorithm_name(algorithm) is not True:
        return validate_algorithm_name(algorithm)

    valid_algorithms = {
        "greedy": greedy_coloring,
        "greedy_bfs": greedy_bfs_coloring,
        "backtrack": find_min_k_backtracking
    }
    
    try:
        coloring_result = valid_algorithms[algorithm](graph)
    except Exception as e:
        return jsonify({
            'message': f'Error occured while executing the {algorithm} algorithm: {str(e)}'
        }), 500
    
    return jsonify({
        'result': coloring_result
    }), 200

@app.route('/analysis/scalability')
def analyse_scalability():
    data = request.get_json()
    algorithm_name = data.get('algorithm')
    density = data.get('density')
    
    if density < 0  or density > 1:
        return jsonify({'message': 'Density must be a value between 0 and 1'})

    if validate_algorithm_name(algorithm_name) is not True:
        return validate_algorithm_name(algorithm_name)
    # Run Experiment

    algorithms = valid_algorithms()
    try:
        algorithm = algorithms[algorithm_name]
        experiment_result = analyse_algorithm_scalability(algorithm, density)
    except Exception as e:
        return jsonify({
            'message': f'Error occured while executing the {algorithm_name} algorithm: {str(e)}'
        }), 500




if __name__ == '__main__':
    app.run(debug=True)
