import traceback

from utils.generate_graph import generate_graph_ne
from utils.utils import ND_to_NE, DE_to_NE

def get_graphs(graph_type: str, N: str, E: str, D: str, num_graphs: int, db_manager):
    N = int(N) if N else None
    D = float(D) if D else None
    E = int(E) if E else None
    #TODO add validation that exactly 2 of N,D,E are present and the third is None
    print(N,D,E)
    if not D:
        return get_graphs_ne(graph_type, N, E, num_graphs, db_manager)
    elif not E:
        return get_graphs_nd(graph_type, N, D, num_graphs, db_manager)
    elif not N:
        return get_graphs_de(graph_type, D, E, num_graphs, db_manager)

def get_graphs_de(graph_type, D, E, num_graphs, db_manager):
    N, E = DE_to_NE(D, E)

    return get_graphs_ne(graph_type, N, E, num_graphs, db_manager)

def get_graphs_nd(graph_type, N, D, num_graphs, db_manager):
    N, E = ND_to_NE(N, D)

    return get_graphs_ne(graph_type, N, E, num_graphs, db_manager)

def get_graphs_ne(graph_type, N, E, num_graphs, db_manager):
    graphs = []
    remaining_graphs = num_graphs

    try:
        existing_graphs = db_manager.find_graphs(graph_type, N, E, num_graphs)
        existing_count = len(existing_graphs)
        print(f"Found {existing_count} graphs out of {num_graphs} requested matching the criteria type={graph_type}, N={N}, E={E}")
        remaining_graphs = num_graphs - existing_count

        for graph in existing_graphs:
            graphs.append(graph)

    except Exception as e:
        print(f"An error occured fetching existing graphs: {e} \n {traceback.format_exc()}")
    
    if remaining_graphs > 0:
        print(f"Generating {remaining_graphs} graphs matching the criteria type={graph_type}, N={N}, E={E}")

    for _ in range(remaining_graphs):

        graph = generate_graph_ne(N, E, db_manager)
        graphs.append(graph)
    
    return graphs

def get_graph_custom(graph_id: str, db_manager):
    """
    Returns the 'graph' field from the MongoDB doc for a custom graph with the given _id.
    Raises ValueError if not found.
    """
    doc = db_manager.get_graph_by_id(graph_id)
    return doc



def get_graphs_from_definitions(graph_definitions, db_manager):
    ""
    graphs = []
    for graph in graph_definitions:
        if graph['type'] != 'custom':
            graphs.append( 
                get_graphs(graph['type'], graph['nodes'], graph['edges'], graph['density'], 1, db_manager)[0]
            )
        
        else:
            graph_id = graph.get('customGraphId')
            if not graph_id:
                raise ValueError("Missing 'customGraphId' for custom graph definition.")

            # Use the new helper
            custom_graph = get_graph_custom(graph_id, db_manager)
            graphs.append(custom_graph)

    return graphs