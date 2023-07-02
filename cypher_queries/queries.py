adv_per_loc_query = '''
MATCH (a:AdversePerson {lower_name: 'marian kocner'})--(l:Location)
WITH COLLECT(l.name) AS locations, COUNT(*) AS totalArticles
RETURN {totalArticles: totalArticles, locations: locations} AS result;
'''

adv_per_articles_query = '''
MATCH (a:AdversePerson {lower_name: $lower_name})--(article:Article)
RETURN article;
'''