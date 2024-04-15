from flask import Flask, request, jsonify, render_template
from modules.Function_Calling_Sql import chat_completion_request
from modules.Function_Calling_Sql import database_schema_string
from modules.Function_Calling_Sql import excel_info
from modules.Function_Calling_Sql import execute_function_call
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

app = Flask(__name__)

database_info = excel_info("Bladenmatrix.xlsx")

tools = [
    {
        "type": "function",
        "function": {
            "name": "ask_database",
            "description": "Gebruik deze functie ALLEEN om Producten in de offerte table te zetten via een SQL query. Bij vragen over de producten maak je GEEN gebruik van deze functie.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"""
                               
                                SQL moet geschreven worden volgens dit database schema:
                                {database_schema_string}
                                The query should be returned in plain text, not in JSON.
                                HET IS OOK HEEL BELANGRIJK DAT JE CHECKT OF WAT ER GEVRAAGD WORDT MOGELIJK IS, BIJVOORBEELD, ALS ER BIJ EEN OFFERTE MET HET MATERIAALSOORT TAURUS TERRAZO WHITE VERZOET WORDT GEVRAAGD, MAG HET NIET ZO ZIJN DAT ER BOORGATEN TOEGEVOEGD KUNNEN WORDEN AAN DE OFFERTE! TEN ALLE TIJDEN NIET!, GEEF DAN ALS INPUT DAT HET NIET MOGELIJK IS OM BOORGATEN TOE TE VOEGEN AAN DE OFFERTE.
                                ALS EEN VRAAG GAAT OVER EEN MATERIAALSOORT MOET JE MEESTAL KIJKEN IN DE TABLE bladmatrix, ALS DE VRAAG GAAT OVER EEN OFFERTE MOET JE MEESTAL KIJKEN IN DE TABLE OFFERTE.
                                Als de offerte tabel moet veranderen gebruik dan alleen de UPDATE statement en gebruik nooit de INSERT, er mag maar 1 ROW blijven ten alle tijden in de offerte tabel.
                                Als je op WCD(wandcontactdoos) moet zoeken, noteer het dan op deze manier: "WCD_(Wandcontactdoos)", anders werkt het niet
                                JE HOEFT NOOIT ZELF EEN PRIJS IN TE VOEREN IN DE OFFERTE, DIT WORDT AUTOMATISCH GEDAAN, DUS BETREK DIT NOOOOIT IN JE SQL STATEMENT. Dus nooit een query maken voor de offerte_prijs waar je zelf een prijs invoert.
                                ZET OOK ALLLEEE KOLOM NAMEN TUSSEN APOSTROFEN, DUS 'kolomnaam' NIET kolomnaam.
                                WANNEER EEN RANDAFWERKING OF IETS DERGELIJKS NIET GEWENST IS IN DE OFFERTE MOET JE DIT OP NULL ZETTEN DUS NIET ALS NIET GEWENST MAAR ECHT OP NULL.

                                """,
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
    print(offerte_list)
    return jsonify(offerte_list)


@app.route('/send_message', methods=['POST'])
def chat():
    import json
    data = request.json
    message_content = data['message']

    # Maak de berichtenlijst voor deze aanvraag; verondersteld dat je dit per sessie of aanvraag beheert
    messages = [{"role": "user", "content": message_content}]
    # Hier voeg je de systeemboodschap toe, zoals je eerder deed
    messages.append({"role": "system", "content": f"Beantwoord de vragen Super netjes en beleefd. Je werkt bij BlisDigital. Dit is de huidige Database van de offerte: \n" + database_schema_string + "\nJe mag alleen SQL Queries gebruiken om producten toe te voegen aan de offerte, anders mag dit ten alle tijden NIET! En moet je dus gewoon op basis van de info je antwoord geven. Als iets niet mogelijk is met een bepaalde materiaalsoort mag je dus ook ten alle tijden het niet mogelijk maken in de offerte."})
    
    chat_completion = chat_completion_request(messages=messages, tools=tools)

    assistant_message = chat_completion.choices[0].message
    if assistant_message.tool_calls:
            results = execute_function_call(assistant_message)
            messages.append({"role": "function", "tool_call_id": assistant_message.tool_calls[0].id, "name": assistant_message.tool_calls[0].function.name, "content": results})
            print(results)
            response_content = "Succesvol uitgevoerd!" + results
        
    else:
        response_content = chat_completion.choices[0].message.content
            
    
    # Extract de chat response van het chat_completion object
    
    print(response_content)

    # Stuur de geëxtraheerde chat response terug naar de client
    return jsonify({'response': response_content})


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()