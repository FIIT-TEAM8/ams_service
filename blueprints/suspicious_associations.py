from flask import Blueprint, request
from flask.json import jsonify
from py2neo import Graph
from unidecode import unidecode
from cypher_queries.queries import susy_assoc_articles_query
import settings

suspicious_associations = Blueprint('suspicious_associations', __name__, url_prefix='/suspicious-associations')

graph = Graph(f'bolt://{settings.NEO4J_BOLT_URL}:{settings.NEO4J_BOLT_PORT}',
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))

@suspicious_associations.route('/search', methods=['GET'])
def search():
    name = request.args.get('name', type=str)

    if name == None:
        return jsonify({
            'message': 'Provide "name" parameter'
        }), 400
    
    cursor = graph.run(susy_assoc_articles_query, lower_name=unidecode(name.lower()))
    query_data = [record['adverse_entity_name'] for record in cursor.data()]

    return jsonify(query_data), 200