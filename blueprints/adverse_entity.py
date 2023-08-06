from flask import Blueprint, request
from flask.json import jsonify
from py2neo import Graph
from unidecode import unidecode
from cypher_queries.queries import adv_ent_loc_query, adv_ent_articles_query
import settings

adverse_entity = Blueprint('adverse_entity', __name__, url_prefix='/adverse-entity')

graph = Graph(f'bolt://{settings.NEO4J_BOLT_URL}:{settings.NEO4J_BOLT_PORT}',
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))


def remove_lower_name_from_lists(lower_name, article_data, ascii_column, non_ascii_column):
    index = article_data[ascii_column].index(lower_name)
    article_data[ascii_column].pop(index)
    article_data[non_ascii_column].pop(index)

    return article_data


def remove_search_ent_from_orgs_and_names(lower_name, cursor_data):
    articles = []

    for record in cursor_data:
        article_data = record['article']

        if lower_name in article_data['gpt3_names_ascii']:
            article_data = remove_lower_name_from_lists(lower_name, article_data,
                                                        'gpt3_names_ascii', 'gpt3_names')

        if lower_name in article_data['gpt3_organizations_ascii']:
            article_data = remove_lower_name_from_lists(lower_name, article_data, 
                                                        'gpt3_organizations_ascii', 'gpt3_organizations')

        articles.append(article_data)

    return articles


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

    lower_name = unidecode(name.lower())
    cursor = graph.run(adv_ent_articles_query, lower_name=lower_name)
    query_data = remove_search_ent_from_orgs_and_names(lower_name, cursor.data())

    return jsonify(query_data), 200