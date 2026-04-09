from flask import Flask, jsonify, request
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client.mydatabase
players_collection = db.players

def merge_csv_to_db(csv_file):
    df = pd.read_csv(csv_file)
    players_from_csv = df.to_dict(orient="records")
    
    updated_count = 0
    for player in players_from_csv:
        # Unikāls ieraksts pēc password+name+character
        filter_query = {
            "password": player["password"],
            "name": player["name"],
            "character": player["character"]
        }
        existing = players_collection.find_one(filter_query)
        if existing:
            # Salīdzina statistiku, piemēram, wave
            if player.get("wave",0) > existing.get("wave",0):
                players_collection.update_one(filter_query, {"$set": player})
                updated_count += 1
        else:
            # Ja nav ieraksta, pievieno jaunu
            players_collection.insert_one(player)
            updated_count += 1
    return updated_count

@app.route('/')
def index():
    return "CSV → MongoDB merge API darbojas!"

@app.route('/sync_csv', methods=['POST'])
def sync_csv():
    try:
        # Pieņem CSV faila ceļu no POST pieprasījuma JSON vai var hardcode
        csv_file = "players.csv"  # vari arī ņemt request.files
        updated_count = merge_csv_to_db(csv_file)

        # Pēc tam atjauno CSV failu no MongoDB, lai visiem būtu vienādi dati
        all_players = list(players_collection.find({}, {"_id":0}))
        pd.DataFrame(all_players).to_csv("players.csv", index=False)

        return jsonify({
            "message": "CSV dati apvienoti ar MongoDB un CSV atjaunināts!",
            "records_updated_or_added": updated_count,
            "total_records": len(all_players)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)