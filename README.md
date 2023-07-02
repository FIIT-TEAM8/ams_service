# OpenAPI specification
https://app.swaggerhub.com/apis/ykbhlvck/advesea-ams-service/1.0.0

# How to run
* python3 -m venv ./venv
* source ./venv/bin/activate
* pip install -r requirements.txt
* add parsed_articles_sk_merged_2018_2019 to root folder
* make sure your neo4j is running
* use env variables according to settings.py for successfull connection to neo4j
* python3 ./data_loader.py
* python3 ./app.py

# Routes
* /adverse-person/search?name=<name-value>
* /adverse-person/detail?name=<name-value>

## Examples
* /adverse-person/search?name=Marian Kocner
* /adverse-person/detail?name=Marian Kocner