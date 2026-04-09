from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Savienojums ar lokālo MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.mydatabase  # Aizvieto ar savu datubāzes nosaukumu
users = db.users  # Kolekcija "users"

@app.route('/')
def index():
    return "Sveiki! MongoDB Flask API darbojas."

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    if not data or 'name' not in data or 'age' not in data:
        return jsonify({"error": "Nepieciešams 'name' un 'age' laukus"}), 400
    # Ievieto datus MongoDB
    result = users.insert_one({"name": data['name'], "age": data['age']})
    return jsonify({"message": "Lietotājs pievienots", "id": str(result.inserted_id)}), 201

@app.route('/users', methods=['GET'])
def get_users():
    all_users = []
    for user in users.find():
        all_users.append({"id": str(user["_id"]), "name": user["name"], "age": user["age"]})
    return jsonify(all_users), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)