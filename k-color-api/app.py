from flask import Flask, jsonify, request
from flask_cors import CORS
import traceback

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
        print(algorithm_names)
        for algorithm_name in algorithm_names:
            print(algorithm_name)
            # print(algorithm_name)
            algorithm = algorithms[algorithm_name]
            experiment_result.update({algorithm_name: analyse_algorithm_scalability(algorithm, density, node_sizes, repeats)})
            print(experiment_result.keys())
        return experiment_result
    except Exception as e:
        return jsonify({
            'message': f'Error occured while executing the {algorithm_name} algorithm: {str(e)} \n {traceback.format_exc()}'
        }), 500




if __name__ == '__main__':
    app.run(debug=True)
