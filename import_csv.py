import pandas as pd
import sqlite3

def csv_to_sqlite(csv_file, db_name):
    # 1. Nolasa CSV
    df = pd.read_csv(csv_file)
    
    # 2. Savienojas ar SQLite (fails tiks izveidots automātiski)
    conn = sqlite3.connect(db_name)
    
    # 3. Ieraksta datus tabulā "PlayerStats"
    df.to_sql('PlayerStats', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"Dati veiksmīgi ierakstīti {db_name}!")

# Izmantošana:
csv_to_sqlite('data/players.csv', 'game_data.db')