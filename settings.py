import os

NEO4J_BOLT_URL = str(os.getenv('NEO4J_BOLT_URL') or 'localhost:7687')
NEO4J_USERNAME = str(os.getenv('NEO4J_USERNAME') or 'neo4j')
NEO4J_PASSWORD = str(os.getenv('NEO4J_PASSWORD') or 'password')