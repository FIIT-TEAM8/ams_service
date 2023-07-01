import os

APP_PORT = int(os.getenv('APP_PORT') or 5050)

NEO4J_BOLT_URL = str(os.getenv('NEO4J_BOLT_URL') or 'localhost')
NEO4J_BOLT_PORT = str(os.getenv('NEO4J_PORT') or '7687')
NEO4J_USERNAME = str(os.getenv('NEO4J_USERNAME') or 'neo4j')
NEO4J_PASSWORD = str(os.getenv('NEO4J_PASSWORD') or 'password')