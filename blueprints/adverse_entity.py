from flask import Blueprint, request
from flask.json import jsonify
from py2neo import Graph
from unidecode import unidecode
from cypher_queries.queries import adv_ent_loc_query, adv_ent_articles_query
import settings

adverse_entity = Blueprint('adverse_entity', __name__, url_prefix='/adverse-entity')

graph = Graph(f'{settings.NEO4J_BOLT_URL}:{settings.NEO4J_BOLT_PORT}',
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))

@adverse_entity.route('/search', methods=['GET'])
def search():
    name = request.args.get('name', type=str)

    if name == None:
        return jsonify({
            'message': 'Provide "name" parameter'
        }), 400
    
    cursor = graph.run(adv_ent_loc_query, lower_name=unidecode(name.lower()))
    query_data = [dict(record['result']) for record in cursor.data()]

    return jsonify(query_data), 200

@adverse_entity.route('/detail', methods=['GET'])
def detail():
    name = request.args.get('name', type=str)

    if name == None:
        return jsonify({
            'message': 'Provide "name" parameter'
        }), 400

    cursor = graph.run(adv_ent_articles_query, lower_name=unidecode(name.lower()))
    query_data = [dict(record['article']) for record in cursor.data()]

    return jsonify(query_data), 200