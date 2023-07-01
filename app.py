import settings
from flask import Flask
from blueprints.search_adverse_person import search_adverse_person

app = Flask(__name__)
app.register_blueprint(search_adverse_person, name='search_adverse_person')

@app.route('/')
def root():
    return 'Hello from ams_service', 200

if __name__ == '__main__':
    app.run(port=settings.APP_PORT)