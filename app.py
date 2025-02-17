from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import psycopg2
import subprocess

app = Flask(__name__)

# Utiliser l'URL PostgreSQL de Render si disponible, sinon SQLite en local
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("postgresql://asphalt_records:i2XTTixzUFAX3CIdtTPccJ9sRdcFEoqH@dpg-cun9i4tsvqrc7390jcug-a/asphaltrecords_db", "sqlite:///users.db")
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')  # Hachage sécurisé
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()  # Recherche uniquement par username
    if user and check_password_hash(user.password, data['password']):  # Vérification sécurisée du mot de passe
        return jsonify({"message": "Login successful!"}), 200
    return jsonify({"message": "Invalid credentials!"}), 401

@app.route("/")
def home():
    return jsonify({"message": "Welcome to my API!"})

DATABASE_URL = os.environ.get("DATABASE_URL")  # Récupérer la vraie URL depuis les variables d'environnement


conn = psycopg2.connect(DATABASE_URL, sslmode='require')  # Connexion sécurisée

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{"id": user.id, "username": user.username} for user in users]
    return jsonify(users_list)

@app.route('/migrate', methods=['GET'])
def run_migration():
    """Exécute flask db upgrade pour appliquer les migrations."""
    try:
        result = subprocess.run(["flask", "db", "upgrade"], capture_output=True, text=True)
        return f"Migrations exécutées : {result.stdout} {result.stderr}", 200
    except Exception as e:
        return f"Erreur lors de la migration : {str(e)}", 500
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Utilise le port de Render ou 5000 en local
    app.run(debug=False, host="0.0.0.0", port=port)
