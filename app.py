import settings
from flask import Flask
from blueprints.adverse_entity import adverse_entity
from blueprints.suspicious_associations import suspicious_associations

app = Flask(__name__)
app.register_blueprint(adverse_entity, name='adverse_entity')
app.register_blueprint(suspicious_associations, name='suspicious_associations')

@app.route('/')
def root():
    return 'Hello from ams_service', 200

if __name__ == '__main__':
    app.run(port=settings.APP_PORT)