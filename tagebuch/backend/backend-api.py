import os
import json
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

# --- Datenbank Konfiguration ---
# Wird aus den Umgebungsvariablen im Kubernetes Deployment gesetzt
app.config['MYSQL_HOST'] = os.environ.get('MARIADB_SERVICE_HOST', 'mariadb-service')
app.config['MYSQL_USER'] = os.environ.get('MARIADB_USER', 'azubi_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MARIADB_PASSWORD', 'AzubiPasswort')
app.config['MYSQL_DB'] = os.environ.get('MARIADB_DATABASE', 'berichtsheft_db')
app.config['MYSQL_PORT'] = int(os.environ.get('MARIADB_SERVICE_PORT', 3306))

mysql = MySQL(app)

# Funktion zum Erstellen der Tabelle (wird beim Start aufgerufen)
def setup_db():
    try:
        cur = mysql.connection.cursor()
        # Erstellt die Tabelle, wenn sie nicht existiert
        cur.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                entry_date DATE NOT NULL,
                duration DECIMAL(4, 1) NOT NULL,
                text TEXT NOT NULL
            )
        """)
        mysql.connection.commit()
        cur.close()
        print("Datenbank-Tabelle erfolgreich initialisiert.")
    except Exception as e:
        print(f"Fehler bei der Datenbank-Initialisierung: {e}")

# Initialisiere die DB-Tabelle beim ersten Request
with app.app_context():
    setup_db()


@app.route('/api/entries', methods=['GET', 'POST'])
def handle_entries():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        # --- SPEICHERN (POST) ---
        try:
            data = request.json
            date = data['date']
            duration = float(data['duration'])
            text = data['text']

            # SQL INSERT-Befehl
            cur.execute("""
                INSERT INTO entries (entry_date, duration, text)
                VALUES (%s, %s, %s)
            """, (date, duration, text))
            
            mysql.connection.commit()
            cur.close()
            return jsonify({'message': 'Eintrag erfolgreich gespeichert'}), 201

        except Exception as e:
            cur.close()
            return jsonify({'error': 'Fehler beim Speichern des Eintrags', 'details': str(e)}), 400

    elif request.method == 'GET':
        # --- LADEN (GET) ---
        cur.execute("SELECT id, entry_date, duration, text FROM entries ORDER BY entry_date ASC")
        
        # Holen aller Ergebnisse
        result = cur.fetchall()
        cur.close()

        # Konvertiere das Ergebnis in eine Liste von Dictionaries
        entries_list = []
        for row in result:
            entry = {
                'id': row[0],
                'date': row[1].strftime('%Y-%m-%d'), # Formatiere das Datum
                'duration': float(row[2]),
                'text': row[3]
            }
            entries_list.append(entry)

        return jsonify(entries_list)

if __name__ == '__main__':
    # Füge CORS hinzu, da Frontend und Backend unterschiedliche Adressen haben
    # Dies ist in Flask etwas aufwendiger, in Express.js einfacher.
    # Für Minikube lassen wir es jetzt weg und konfigurieren den Ingress später.
    app.run(host='0.0.0.0', port=5000)