from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import psycopg2

app = Flask(__name__)

# Utiliser l'URL PostgreSQL de Render si disponible, sinon SQLite en local
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("postgresql://asphalt_records:i2XTTixzUFAX3CIdtTPccJ9sRdcFEoqH@dpg-cun9i4tsvqrc7390jcug-a/asphaltrecords_db", "sqlite:///users.db")
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Créez la base de données
with app.app_context():
    db.create_all()

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

# Connexion à la base de données
conn = psycopg2.connect(
    dbname="votre_dbname",
    user="votre_user",
    password="votre_password",
    host="votre_host",
    port="votre_port"
)

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{"id": user.id, "username": user.username} for user in users]
    return jsonify(users_list)



# Création d'un curseur pour exécuter des requêtes
cur = conn.cursor()

# Exécution d'une requête SQL
cur.execute("SELECT version();")
db_version = cur.fetchone()
print("Version de PostgreSQL :", db_version)

# Fermeture de la connexion
cur.close()
conn.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Utilise le port de Render ou 5000 en local
    app.run(debug=False, host="0.0.0.0", port=port)
