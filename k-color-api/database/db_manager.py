import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
from typing import Dict, List, Optional
import time
import functools

def timer(func):
    """
    Decorator that measures and prints the execution time of the decorated function.
    """
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds.")
    return wrapper_timer

class MongoDBManager:
    @timer
    def __init__(self):
        """
        Initializes the MongoDBManager with URI, database name, and collection name from .env.
        """
        load_dotenv()

        username = os.getenv('MONGO_USERNAME')
        password = os.getenv('MONGO_PASSWORD')
        cluster_url = os.getenv('MONGO_CLUSTER_URL')
        database_name = os.getenv('MONGO_DATABASE_NAME')

        if not all([username, password, cluster_url, database_name]):
            raise ValueError("One or more MongoDB environment variables are missing.")

        connection_string = f"mongodb+srv://{username}:{password}@{cluster_url}/{database_name}?retryWrites=false&w=1&maxPoolSize=200&connectTimeoutMS=3000&socketTimeoutMS=30000&serverSelectionTimeoutMS=5000&readPreference=primaryPreferred&heartbeatFrequencyMS=5000"

        self.conn_str = connection_string
        self.db_name = database_name
        self.collection_name = "graphs"
        self.client: Optional[MongoClient] = None
        self.collection: Optional[MongoClient] = None
        self.connect()

    @timer
    def connect(self):
        """
        Establishes a connection to the MongoDB server.
        """
        try:
            self.client = MongoClient(self.conn_str, serverSelectionTimeoutMS=5000)  # 5-second timeout
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            self.collection = self.client[self.db_name][self.collection_name]
            print("Connected to MongoDB successfully.")
            self.create_indexes()
        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            raise

    @timer
    def save_graph(self, graph_data: Dict):
        """
        Saves the graph data to the MongoDB collection.
        """
        if self.collection is None:
            raise Exception("MongoDB collection is not initialized.")
        
        try:
            result = self.collection.insert_one(graph_data)
            print(f"Graph {graph_data['name']} saved with _id: {result.inserted_id}")
        except Exception as e:
            print(f"An error occurred while saving the graph: {e}")
            raise

    @timer
    def find_graphs(self, graph_type: str, N: int, E: int, limit: int) -> List[Dict]:
        """
        Finds and returns graphs matching the given query.
        Returns a list of graph adjacency lists.
        """
        if self.collection is None:
            raise Exception("MongoDB collection is not initialized.")
        
        query = {
            "graph_type": graph_type,
            "N": N,
            "E": E
        }
        projection = {
            "graph": 1
        }

        try:
            cursor = self.collection.find(query, projection).limit(limit)
            graphs = list(cursor)
            return graphs
        except Exception as e:
            print(f"An error occurred while fetching graphs: {e}")
            raise

    @timer
    def create_indexes(self):
        """
        Creates indexes on frequently queried fields to optimize performance.
        """
        if self.collection is None:
            raise Exception("MongoDB collection is not initialized.")
        
        self.collection.create_index("graph_type")
        self.collection.create_index("num_nodes")
        self.collection.create_index("num_edges")
        print("Indexes created on 'graph_type', 'num_nodes', and 'num_edges'.")

    @timer
    def close_connection(self):
        """
        Closes the MongoDB connection.
        """
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")
