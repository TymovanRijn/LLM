import pandas as pd
import sqlite3

# Stap 1: Lees het Excel-bestand
excel_path = 'Bladenmatrix.xlsx'  # Pas dit pad aan naar jouw bestand
df = pd.read_excel(excel_path, header=1, sheet_name='Bladenmatrix')  # Pas de sheet_name aan indien nodig

# Verwijder de 'Unnamed: 0' kolom als deze bestaat
if 'Unnamed: 0' in df.columns:
    df.drop('Unnamed: 0', axis=1, inplace=True)

# Vervang spaties in kolomnamen door onderstrepingstekens
df.columns = [col.replace(" ", "_") for col in df.columns]

# Verbinden met SQLite-database
conn = sqlite3.connect('./data/Offerte.sql')  # Zorg ervoor dat dit het pad is waar je je database wilt hebben
cursor = conn.cursor()

# # Stap 2: Maak de SQL-tabel Bladenmatrix en vul deze met data uit de DataFrame
# # Als de tabel al bestaat, verwijder deze dan eerst
# cursor.execute('DROP TABLE IF EXISTS Bladenmatrix')

# # Gebruik pandas to_sql functie om de DataFrame in een SQL-tabel te zetten
# df.to_sql('Bladenmatrix', conn, if_exists='replace', index=False)

#Clear row 2 in table offerte
cursor.execute('ALTER TABLE Bladenmatrix RENAME COLUMN "WCD_(Wandcontactdoos)" TO WCD_Wandcontactdoos;')

# Commit en sluit de database connectie
conn.commit()
conn.close()

print("De Bladenmatrix is succesvol in de SQL-tabel geladen.")
