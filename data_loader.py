import json
import settings
from unidecode import unidecode
from py2neo import Graph, Node, Relationship

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

with open('parsed_articles_sk_merged_2018_2019.jl', 'r') as file:
    for line in file:
        article_data = json.loads(line)

        if article_data['gpt3_adverse_behaviour'] == {}:
            continue
        
        org_with_assoc = article_data['gpt3_organizations'] if type(article_data['gpt3_organizations']) == list \
            else list(article_data['gpt3_organizations'])

        # process gpt3_entities
        if 'names' in article_data['gpt3_entities']:
            article_data['gpt3_names'] = article_data['gpt3_entities']['names'] \
                if type(article_data['gpt3_entities']['names']) == list else []
        if 'geographical_places' in article_data['gpt3_entities']:
            article_data['gpt3_locations'] = article_data['gpt3_entities']['geographical_places']
        if 'organizations' in article_data['gpt3_entities']:
            article_data['gpt3_organizations'] = article_data['gpt3_entities']['organizations'] \
                if type(article_data['gpt3_entities']['organizations']) == list else []
        del article_data['gpt3_entities']
        
        gpt3_adverse_behaviour = article_data['gpt3_adverse_behaviour']
        article_data['adverse_behaviour'] = gpt3_adverse_behaviour['adverse_behaviour'] if 'adverse_behaviour' in gpt3_adverse_behaviour \
            else gpt3_adverse_behaviour['adverse_behavior']
        del article_data['gpt3_adverse_behaviour']

        # create article node
        article_node = Node('Article', **article_data)
        graph.create(article_node)

        for org_data in org_with_assoc:
            if type(org_data) != dict or org_data == {}:
                continue

            
            org_node = graph.run(get_org_query, lower_name=unidecode(org_data['organization'].lower())).evaluate()
            if not org_node:
                org_node = Node('Organization', name=org_data['organization'],
                                        lower_name=unidecode(org_data['organization'].lower()))

            if 'associates' in org_data:
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
            