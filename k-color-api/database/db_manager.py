import os
import multiprocessing
from bson import ObjectId
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
        Only connects if running in the main thread.
        """
        if multiprocessing.current_process().name != "MainProcess":
            return None
        load_dotenv()

        username = os.getenv('MONGO_USERNAME')
        password = os.getenv('MONGO_PASSWORD')
        cluster_url = os.getenv('MONGO_CLUSTER_URL')
        database_name = os.getenv('MONGO_DATABASE_NAME')

        if not all([username, password, cluster_url, database_name]):
            raise ValueError("One or more MongoDB environment variables are missing.")

        connection_string = (
            f"mongodb+srv://{username}:{password}@{cluster_url}/{database_name}"
            "?retryWrites=false&w=1&maxPoolSize=200&connectTimeoutMS=3000"
            "&socketTimeoutMS=30000&serverSelectionTimeoutMS=5000"
            "&readPreference=primaryPreferred&heartbeatFrequencyMS=5000"
        )

        self.conn_str = connection_string
        self.db_name = database_name
        self.collection_name = "graphs"
        self.client: Optional[MongoClient] = None
        self.collection: Optional[MongoClient] = None
        self.connect()


        # Only connect if we're in the main thread.
        # print("Thread: ",multiprocessing.current_process().name)
        # if multiprocessing.current_process().name == "MainProcess":
        #     self.connect()
        # else:
        #     print("Not in main thread; skipping MongoDB connection.")

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
            return result.inserted_id
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
            "graph": 1,
            "id": 1,
            "chromatic_number": 1
        }

        try:
            cursor = self.collection.find(query, projection).limit(limit)
            graphs = list(cursor)
            return graphs
        except Exception as e:
            print(f"An error occurred while fetching graphs: {e}")
            raise
    
    @timer
    def get_graph_by_id(self, graph_id: str) -> dict:
        """
        Finds a single graph document by its MongoDB _id (as string).
        Returns a dict with the entire document.
        Raises ValueError if not found or invalid ObjectId.
        """
        if self.collection is None:
            raise Exception("MongoDB collection is not initialized.")

        try:
            _id = ObjectId(graph_id)  
        except Exception as e:
            raise ValueError(f"Invalid graph_id '{graph_id}': {str(e)}")

        try:
            doc = self.collection.find_one({"_id": _id}, {
                "graph": 1, "name": 1, "N": 1, "E": 1, "_id": 1, 
                "chromatic_number": 1, "description": 1
            })
            if not doc:
                raise ValueError(f"No graph found with _id={graph_id}")
            doc['_id'] = str(doc['_id'])
            return doc
        except Exception as e:
            print(f"An error occurred while finding graph by id: {graph_id}. Error: {e}")
            raise
    
    @timer
    def upsert_field(self, graph_id: str, field_name: str, field_value, upsert: bool = False) -> Dict:
        """
        Upserts a field in the document with the given graph_id.
        """
        if self.collection is None:
            raise Exception("MongoDB collection is not initialized.")

        try:
            _id = ObjectId(graph_id)
        except Exception as e:
            raise ValueError(f"Invalid graph_id '{graph_id}': {str(e)}")

        try:
            result = self.collection.update_one(
                {"_id": _id},
                {"$set": {field_name: field_value}},
                upsert=upsert
            )
            if result.matched_count == 0 and not upsert:
                raise ValueError(f"No graph found with _id={graph_id}")
            operation_result = {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None
            }
            if result.upserted_id:
                print(f"Document inserted with _id: {result.upserted_id}")
            else:
                print(f"Field '{field_name}' updated to '{field_value}' for graph with _id={graph_id}.")
            return operation_result
        except Exception as e:
            print(f"An error occurred while upserting field: {e}")
            raise
    
    @timer
    def get_custom_graphs(self, search: str, page: int, limit: int) -> dict:
        """
        Returns paginated list of custom graphs, optionally filtered by name.
        """
        if self.collection is None:
            raise Exception("MongoDB collection is not initialized.")

        query = {"custom": True}
        if search:
            query["name"] = {"$regex": search, "$options": "i"}

        total = self.collection.count_documents(query)
        skip = (page - 1) * limit
        projection = {"_id": 1, "name": 1}

        try:
            cursor = self.collection.find(query, projection).skip(skip).limit(limit)
            results = [{"id": str(doc["_id"]), "name": doc["name"]} for doc in cursor]
            has_more = (page * limit) < total
            return {
                "results": results,
                "total": total,
                "hasMore": has_more
            }
        except Exception as e:
            print(f"An error occurred while fetching custom graphs: {e}")
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
