from flask import Flask, session, request, jsonify, render_template
from modules.Function_Calling_Sql import chat_completion_request
from modules.Function_Calling_Sql import database_schema_string
from modules.Function_Calling_Sql import excel_info
from modules.Function_Calling_Sql import execute_function_call
from modules.Function_Calling_Sql import update_database_schema_string
from flask_cors import CORS
import uuid
import sqlite3
import os

app = Flask(__name__)
CORS(app)

app = Flask(__name__)
app.secret_key = os.urandom(24)


database_info = excel_info("Bladenmatrix.xlsx")

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_to_offerte_table",
            "description": "Gebruik deze functie ALLEEN om Producten in de offerte table te zetten via een SQL query, veog NOOIT handmatig de prijs toe. Bij vragen over de producten maak je GEEN gebruik van deze functie.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"""
                        Doel: Deze functie is specifiek ontworpen om bestaande gegevens binnen de 'offerte' tabel via een SQL query te wijzigen. Gebruik deze functie met de volgende beperkingen en richtlijnen in acht:

Kernrichtlijnen:
Prijsbeheer: Voeg nooit zelf prijsinformatie toe aan de query. Alle prijzen worden automatisch berekend door het systeem.
Identificatiebeheer: De ID van de te bewerken rij is altijd 1. Je hoeft de ID-waarde niet aan te passen in je queries.
Rijverwijdering Verboden: Het is strikt verboden om hele rijen uit de 'offerte' tabel te verwijderen. Elke poging om een DELETE statement uit te voeren die een hele rij beïnvloedt, is niet toegestaan en zal resulteren in een foutmelding.
Belangrijke Waarschuwingen:
Het verwijderen van hele rijen uit de offerte tabel is ten strengste verboden. Elke poging hiertoe wordt geblokkeerd en resulteert in een foutmelding.
Validatiestappen:
Delete Operatie Controle: Zorg ervoor dat de SQL-query geen DELETE operatie bevat die een hele rij zou verwijderen.
Materiaalsoort Controle: Vergelijk de 'materiaalsoort' gespecificeerd in de query met de restrictielijst om te verzekeren dat de wijziging toegestaan is.
Restrictie Response: Als een operatie niet is toegestaan vanwege de materiaalsoortrestricties, of als een poging wordt gedaan om een hele rij te verwijderen, geef dan de volgende foutmelding: "Operatie niet toegestaan; poging om hele rij te verwijderen of restrictie op materiaalsoort."
Uitvoering: Voer de SQL-query alleen uit als deze voldoet aan alle bovenstaande veiligheids- en validatiechecks.
Gebruiksinstructies:
Query Formaat: Gebruik UPDATE statements om gegevens in de offerte aan te passen. Omring kolomnamen altijd met apostrofen, bijvoorbeeld 'kolomnaam'.
Onnodige Eigenschappen: Voor eigenschappen die niet langer gewenst zijn, stel deze in op NULL in plaats van ze te verwijderen.
Voorbeeld van een Correcte Query:
sql
Copy code
UPDATE offerte SET 'detail' = 'waarde' WHERE 'materiaalsoort' = 'toegestaan materiaal';
Dit voorbeeld toont hoe je specifieke gegevens binnen een offerte veilig kunt aanpassen, met naleving van de gestelde beperkingen.""",
                    }
                },
                "required": ["query"],
            },
        }
    }
]

messages = []


def get_db_connection():
    conn = sqlite3.connect('./data/Offerte.sql')
    conn.row_factory = sqlite3.Row  # Maakt het mogelijk om kolomheaders te gebruiken
    return conn

@app.route('/get_offerte_data')
def get_offerte_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM offerte_prijs WHERE ID=1')  # Update de query indien nodig
    offerte_items = cur.fetchall()

    # Converteer de resultaten naar een lijst van dicts zodat jsonify ze kan verwerken
    offerte_list = [dict(ix) for ix in offerte_items]

    conn.close()
    # print(offerte_list)
    return jsonify(offerte_list)


@app.route('/send_message', methods=['POST'])
def chat():
    database_schema_string = update_database_schema_string()
    data = request.json
    message_content = data['message']

    # Maak de berichtenlijst voor deze aanvraag; verondersteld dat je dit per sessie of aanvraag beheert
    messages = [{"role": "user", "content": message_content}]
    # Hier voeg je de systeemboodschap toe, zoals je eerder deed
    print(f"DIT IS DE DATABASE STRING: {database_schema_string}")
    messages.append({"role": "system", "content": f"Beantwoord de vragen Super netjes en beleefd. Je werkt bij BlisDigital. Dit is de huidige Database van de offerte: \n" + database_schema_string + "\nJe mag alleen SQL Queries gebruiken om producten toe te voegen aan de offerte, anders mag dit ten alle tijden NIET! En moet je dus gewoon op basis van de info je antwoord geven. Als iets niet mogelijk is met een bepaalde materiaalsoort mag je dus ook ten alle tijden het niet mogelijk maken in de offerte."})
    
    chat_completion = chat_completion_request(messages=messages, tools=tools)

    assistant_message = chat_completion.choices[0].message
    if assistant_message.tool_calls:
            results = execute_function_call(assistant_message)
            messages.append({"role": "function", "tool_call_id": assistant_message.tool_calls[0].id, "name": assistant_message.tool_calls[0].function.name, "content": results})
            # print(results)
            print("RESULTS: " + results)
            if "HELAAS IS DEZE WIJZIGING NIET MOGELIJK" in results.upper():
                response_content = "Helaas is deze wijziging niet mogelijk."
            else:
                response_content = "Succesvol uitgevoerd!"
        
    else:
        response_content = chat_completion.choices[0].message.content
            
    
    # Extract de chat response van het chat_completion object
    
    # print(response_content)

    # Stuur de geëxtraheerde chat response terug naar de client
    return jsonify({'response': response_content})


@app.route('/')
def home():
    if 'UserSession' not in session:
        session['UserSession'] = str(uuid.uuid4())
    print("UserSession ID: ", session['UserSession'])
    return render_template('index.html')

if __name__ == '__main__':
    app.run()