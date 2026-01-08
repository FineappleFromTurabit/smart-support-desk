# app.py
from flask import Flask
from routes.customers import customers_bp
from flasgger import Swagger
from routes.auth import auth_bp

app = Flask(__name__)
Swagger(app)
from routes.tickets import tickets_bp

app.register_blueprint(tickets_bp)
from routes.dashboard import dashboard_bp

app.register_blueprint(dashboard_bp)


app.register_blueprint(customers_bp)

app.register_blueprint(auth_bp)
if __name__ == "__main__":
    app.run(debug=True)
    