from flask import Blueprint, request
from flask.json import jsonify
from py2neo import Graph
from unidecode import unidecode
from cypher_queries.queries import adv_per_loc_query, adv_per_articles_query
import settings

adverse_person = Blueprint('adverse_person', __name__, url_prefix='/adverse-person')

graph = Graph(f'{settings.NEO4J_BOLT_URL}:{settings.NEO4J_BOLT_PORT}',
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))

@adverse_person.route('/search', methods=['GET'])
def search():
    name = request.args.get('name', type=str)

    if name == None:
        return jsonify({
            'message': 'Provide "name" parameter'
        }), 400
    
    cursor = graph.run(adv_per_loc_query, lower_name=unidecode(name.lower()))
    query_data = cursor.data()

    return jsonify(query_data), 200

@adverse_person.route('/detail', methods=['GET'])
def detail():
    name = request.args.get('name', type=str)

    if name == None:
        return jsonify({
            'message': 'Provide "name" parameter'
        }), 400

    cursor = graph.run(adv_per_articles_query, lower_name=unidecode(name.lower()))
    query_data = cursor.data()

    return jsonify(query_data), 200