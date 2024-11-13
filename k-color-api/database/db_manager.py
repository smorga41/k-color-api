import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
from typing import Dict

class MongoDBManager:
    def __init__(self):
        """
        Initializes the MongoDBManager with URI, database name, and collection name from .env.
        """
        load_dotenv()

        username = os.getenv('MONGO_USERNAME')
        password = os.getenv('MONGO_PASSWORD')
        cluster_url = os.getenv('MONGO_CLUSTER_URL')
        database_name = os.getenv('MONGO_DATABASE_NAME')

        connection_string = f"mongodb+srv://{username}:{password}@{cluster_url}/{database_name}?retryWrites=true&w=majority"

        self.conn_str = connection_string
        self.db_name = database_name
        self.collection_name = "graphs"
        self.client = None
        self.collection = None
        self.connect()

    def connect(self):
        """
        Establishes a connection to the MongoDB server.
        """
        try:
            self.client = MongoClient(self.conn_str)
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            self.collection = self.client[self.db_name][self.collection_name]
            print("Connected to MongoDB successfully.")
        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            raise

    def save_graph(self, graph_data: Dict):
        """
        Saves the graph data to the MongoDB collection.
        """
        if self.collection is None:
            raise Exception("MongoDB collection is not initialized.")
        result = self.collection.insert_one(graph_data)
        print(f"Graph saved with _id: {result.inserted_id}")

    def find_graphs(self, query: Dict):
        """
        Finds and returns graphs matching the given query.
        """
        if self.collection is None:
            raise Exception("MongoDB collection is not initialized.")
        
        return self.collection.find(query)

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
    
    def close_connection(self):
        """
        Closes the MongoDB connection.
        """
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")
