from flask import Blueprint, request
from flask.json import jsonify
from py2neo import Graph
from unidecode import unidecode
import settings

search_adverse_person = Blueprint('search_adverse_person', __name__, url_prefix='/adverse-person')

graph = Graph(f'{settings.NEO4J_BOLT_URL}:{settings.NEO4J_BOLT_PORT}',
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))

adv_per_loc_query = '''
MATCH (a:AdversePerson {lower_name: 'marian kocner'})--(l:Location)
WITH COLLECT(l.name) AS locations, COUNT(*) AS totalArticles
RETURN {totalArticles: totalArticles, locations: locations} AS result;
'''

@search_adverse_person.route('/search', methods=['GET'])
def search():
    name = request.args.get('name', type=str)

    if name == None:
        return jsonify({
            'message': 'Provide "name" parameter'
        }), 400
    
    cursor = graph.run(adv_per_loc_query, lower_name=unidecode(name.lower()))
    query_data = cursor.data()

    return jsonify(query_data), 200

