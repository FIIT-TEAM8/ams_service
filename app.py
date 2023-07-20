import settings
from flask import Flask
from blueprints.adverse_person import adverse_entity

app = Flask(__name__)
app.register_blueprint(adverse_entity, name='adverse_entity')

@app.route('/')
def root():
    return 'Hello from ams_service', 200

if __name__ == '__main__':
    app.run(port=settings.APP_PORT)