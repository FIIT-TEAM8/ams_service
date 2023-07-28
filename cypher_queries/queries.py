adv_ent_loc_query = '''
MATCH (a:AdverseEntity {lower_name: $lower_name})--(l:Location)
WITH COLLECT(l.name) AS locations, COUNT(*) AS totalArticles
RETURN {totalArticles: totalArticles, locations: locations} AS result;
'''

adv_ent_articles_query = '''
MATCH (a:AdverseEntity {lower_name: $lower_name})--(article:Article)
RETURN article;
'''

susy_assoc_articles_query = '''
'''