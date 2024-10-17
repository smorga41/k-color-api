from flask import Flask, jsonify, request
from flask_cors import CORS
from algorithms.greedy import greedy_coloring, greedy_bfs_coloring

app = Flask(__name__)
CORS(app)

@app.route('/hello-world')
def get_hello_world():
    return jsonify({"message": "Hello world"})

@app.route('/color-graph/', methods=['POST'])
def greedy_color():
    print("API called ")
    data = request.get_json()
    graph = data.get('graph')
    algorithm = data.get('algorithm', 'greedy')
    
    # validation
    if graph is None:
        return jsonify({"message": "Graph and k must be provided"}), 400
    if not isinstance(graph, dict):
        return jsonify({"message" "Graph must be a dictionary"}), 400
    
    # Ensure graph is adjacency list
    for node, neighbours in graph.items():
        if not isinstance(neighbours, list):
            return jsonify({'message': f'neighbours of node {node} must be a list'}), 400
    
    valid_algorithms = {
        "greedy": greedy_coloring,
        "greedy_bfs": greedy_bfs_coloring
    }
    if algorithm not in valid_algorithms.keys():
        return jsonify({'message': f'Invalid algorithm {algorithm}, Valid options are {', '.join(valid_algorithms.keys())}'})
    
    try:
        coloring_result = valid_algorithms[algorithm](graph)
    except Exception as e:
        return jsonify({
            'message': f'Error occured while executing the {algorithm} algorithm: {str(e)}'
        }), 500
    
    return jsonify({
        'result': coloring_result
    }), 200







if __name__ == '__main__':
    app.run(debug=True)
