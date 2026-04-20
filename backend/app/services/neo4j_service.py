import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, '.env')
load_dotenv(env_path)

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

class Neo4jConnection:
    def __init__(self):
        try:
            # Connect to the Neo4j Aura Database
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Verify connection
            self.driver.verify_connectivity()
            print("\n" + "="*40)
            print("🟢 NEO4J GRAPH DATABASE CONNECTED SUCCESSFULLY!")
            print("="*40 + "\n")
        except Exception as e:
            print(f"\n❌ Neo4j Connection Failed: {e}\n")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def execute_query(self, query, parameters=None):
        if not self.driver:
            print("Cannot execute query. No database connection.")
            return None
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

# Create a global instance to be used across the app
neo4j_db = Neo4jConnection()