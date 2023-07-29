import json
import settings
from unidecode import unidecode
from py2neo import Graph, Node, Relationship


def parse_adverse_behaviour(gpt3_adverse_behaviour):
    adverse_behaviour = []

    if 'adverse_behaviour' in gpt3_adverse_behaviour and type(gpt3_adverse_behaviour['adverse_behaviour']) == list \
        and len(gpt3_adverse_behaviour['adverse_behaviour']) > 0 and type(gpt3_adverse_behaviour['adverse_behaviour'][0]) == dict:
        for adverse_entity_data in gpt3_adverse_behaviour['adverse_behaviour']:
            adverse_behaviour.append(adverse_entity_data['person'])

        return adverse_behaviour

    for _, values in gpt3_adverse_behaviour.items():
        for value in values:
            adverse_behaviour.append(value)

    return adverse_behaviour


def create_ascii_orgs_entities_locations(article_data):
    ascii_non_ascii = {
        'gpt3_names_ascii': 'gpt3_names',
        'gpt3_organizations_ascii': 'gpt3_organizations',
        'gpt3_locations_ascii': 'gpt3_locations'
    }

    for ascii_key, non_ascii_key in ascii_non_ascii.items():
        article_data[ascii_key] = [unidecode(value.lower()) for value in article_data[non_ascii_key]]

    return article_data


graph = Graph(f'{settings.NEO4J_BOLT_URL}:{settings.NEO4J_BOLT_PORT}',
              auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))

get_entity_query = '''
MATCH (a:AdverseEntity {lower_name: $lower_name}) return a;
'''

create_location_query = '''
MERGE (location: Location {name: $name})
RETURN location;
'''

get_org_query = '''
MATCH (org: Organization {lower_name: $lower_name}) RETURN org;
'''

create_org_assoc_query = '''
MERGE (org_assoc: OrganizationAssoc {name: $name, lower_name: $lower_name})
return org_assoc;
'''

file = open('gpt_adverse_articles_lines.json', 'r')
for line in file:
    article_data = json.loads(line)

    if article_data['gpt3_adverse_behaviour'] == {}:
        continue
    
    article_data['_id'] = article_data['_id']['$oid']

    org_with_assoc = article_data['gpt3_organizations'] if type(article_data['gpt3_organizations']) == list \
        else list(article_data['gpt3_organizations'])
    del article_data['gpt3_organizations']

    # process gpt3_entities
    article_data['gpt3_names'] = []
    article_data['gpt3_organizations'] = []
    article_data['gpt3_locations'] = []

    if 'names' in article_data['gpt3_entities'] and type(article_data['gpt3_entities']['names']) == list:
        article_data['gpt3_names'] = article_data['gpt3_entities']['names']
        
    if 'geographical_places' in article_data['gpt3_entities'] and \
        type(article_data['gpt3_entities']['geographical_places']) == list:
        article_data['gpt3_locations'] = article_data['gpt3_entities']['geographical_places']
        
    if 'organizations' in article_data['gpt3_entities'] and \
        type(article_data['gpt3_entities']['organizations']) == list:
        article_data['gpt3_organizations'] = article_data['gpt3_entities']['organizations']

    del article_data['gpt3_entities']
    
    article_data['adverse_behaviour'] = parse_adverse_behaviour(article_data['gpt3_adverse_behaviour'])
    del article_data['gpt3_adverse_behaviour']

    article_data = create_ascii_orgs_entities_locations(article_data)

    # create article node
    article_node = Node('Article', **article_data)
    graph.create(article_node)

    for org_data in org_with_assoc:
        if type(org_data) != dict or org_data == {}:
            continue
        
        org_name = unidecode(org_data['organization'].lower() if 'organization' in org_data else org_data['organisation'].lower())

        org_node = graph.run(get_org_query, lower_name=org_name).evaluate()
        if not org_node:
            org_node = Node('Organization', name=org_name, lower_name=unidecode(org_name.lower()))

        if 'associates' in org_data and org_data['associates']:
            for org_assoc in org_data['associates']:
                if org_assoc == None:
                    continue
                elif type(org_assoc) == dict:
                    org_assoc = org_assoc['name']

                # create organization associate node if doesn't exists
                org_assoc_cursor = graph.run(create_org_assoc_query, name=org_assoc, lower_name=unidecode(org_assoc.lower()))
                org_assoc_node = org_assoc_cursor.data()[0]['org_assoc']

                if not graph.exists(Relationship(org_node, 'ASSOCIATE', org_assoc_node)):
                    # create relationship between organization and associate if doesn't exist
                    graph.create(Relationship(org_node, 'ASSOCIATE', org_assoc_node))

        if not graph.exists(Relationship(article_node, 'CONTAINS', org_node)):
            # create relationship between article and organization if doesn't exist
            graph.create(Relationship(article_node, 'CONTAINS', org_node))

    adverse_people = article_data['adverse_behaviour']
    geo_locations = article_data['gpt3_locations'] if 'gpt3_locations' in article_data else []
    for adverse_entity_name in adverse_people:
        adverse_entity = graph.run(get_entity_query, lower_name=unidecode(adverse_entity_name.lower())).evaluate()

        if not adverse_entity:
            adverse_entity = Node('AdverseEntity', name=adverse_entity_name,
                                    lower_name=unidecode(adverse_entity_name.lower()))
        
        article_entity_rel = Relationship(article_node, 'CONTAINS', adverse_entity)
        graph.create(article_entity_rel)

        for geo_location in geo_locations:
            # create location node if not exists
            location_cursor = graph.run(create_location_query, name=geo_location)
            location_node = location_cursor.data()[0]['location']

            if not graph.exists(Relationship(adverse_entity, 'GEO_ASSOC', location_node)):
                # create relationship between adverse entity and location only if doesn't exist
                entity_location_rel = Relationship(adverse_entity, 'GEO_ASSOC', location_node)
                graph.create(entity_location_rel)
        
file.close()