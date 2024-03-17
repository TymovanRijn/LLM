import pandas as pd
import sqlite3

# Stap 1: Lees het Excel-bestand
excel_path = 'Bladenmatrix.xlsx'  # Pas dit pad aan naar jouw bestand
df = pd.read_excel(excel_path, header=1, sheet_name='Bladenmatrix')  # Pas de sheet_name aan indien nodig

# Verbinden met SQLite-database
conn = sqlite3.connect('./data/Offerte.sql')
cursor = conn.cursor()

# Stap 2: Maak een tabel aan genaamd materiaalsoorten
cursor.execute('''
CREATE TABLE IF NOT EXISTS materiaalsoorten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    materiaalsoort TEXT
)
''')
#insert  Noble Desiree Grey Matt
conn.commit()


# Stap 3: Vul de tabel met de materiaalsoorten
materiaalsoorten = df['Materiaalsoort'].unique()
for materiaalsoort in materiaalsoorten:
    cursor.execute('''
    INSERT INTO materiaalsoorten (materiaalsoort)
    VALUES (?)
    ''', (materiaalsoort,))
conn.commit()
conn.close()
#edit value in row
# cursor.execute("UPDATE materiaal_0 SET 'soort' = 'Hout' WHERE id = 1")

print("Tabellen succesvol aangemaakt en gevuld met gegevens.")
