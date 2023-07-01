import json
import settings
from unidecode import unidecode
from py2neo import Graph, Node, Relationship

graph = Graph(settings.NEO4J_BOLT_URL, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))

create_person_query = '''
MERGE (person: AdversePerson {name: $name, lower_name: $lower_name})
RETURN person;
'''

create_location_query = '''
MERGE (location: Location {name: $name})
RETURN location;
'''

create_org_query = '''
MERGE (org: Organization {name: $name, lower_name: $lower_name})
RETURN org;
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
                if article_data['gpt3_entities']['names'] == list else []
        if 'geographical_places' in article_data['gpt3_entities']:
            article_data['gpt3_locations'] = article_data['gpt3_entities']['geographical_places']
        if 'organizations' in article_data['gpt3_entities']:
            article_data['gpt3_organizations'] = article_data['gpt3_entities']['organizations'] \
                if (article_data['gpt3_entities']['organizations']) == list else []
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

            # create nodes for each organization if doesn't exists
            org_cursor = graph.run(create_org_query, name=org_data['organization'], lower_name=unidecode(org_data['organization'].lower()))
            org_node = org_cursor.data()[0]['org']

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
        for adverse_person_name in adverse_people:
            # create adverse person node if not exists
            person_cursor = graph.run(create_person_query, name=adverse_person_name.lower(),
                                    lower_name=unidecode(adverse_person_name.lower()))
            adverse_person = person_cursor.data()[0]['person']
            
            article_person_rel = Relationship(article_node, 'CONTAINS', adverse_person)
            graph.create(article_person_rel)

            for geo_location in geo_locations:
                # create location node if not exists
                location_cursor = graph.run(create_location_query, name=geo_location)
                location_node = location_cursor.data()[0]['location']

                if not graph.exists(Relationship(adverse_person, 'GEO_ASSOC', location_node)):
                    # create relationship between adverse person and location only if doesn't exist
                    person_location_rel = Relationship(adverse_person, 'GEO_ASSOC', location_node)
                    graph.create(person_location_rel)
            