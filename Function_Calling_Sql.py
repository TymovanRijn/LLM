import sqlite3
import json
from openai import OpenAI

client = OpenAI(
    api_key= "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",	
)
connection = sqlite3.connect('./data/Offerte.sql')
cursor = connection.cursor()
#Delete table Offerte




def get_table_names(conn):
    """Return a list of table names."""
    table_names = []
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for table in tables.fetchall():
        table_names.append(table[0])
    return table_names


def get_column_details(table_name):
    """Return a list of column names with types and default values."""
    column_details = []
    columns = connection.execute(f"PRAGMA table_info('{table_name}');").fetchall()
    for col in columns:
        # Elk item in 'col' representeert een kolom in de tabel, waarbij:
        # col[1] de kolomnaam is, col[2] het datatype, en col[4] de default waarde
        name = col[1]
        data_type = col[2]
        default_val = f"DEFAULT {col[4]}" if col[4] else ""
        column_details.append(f"{name} {data_type} {default_val}".strip())
    return column_details

def get_table_sample_data(table_name, limit=2):
    """Return a sample of table data (first few rows)."""
    try:
        sample_data = connection.execute(f"SELECT * FROM {table_name} LIMIT {limit};").fetchall()
        return sample_data
    except Exception as e:
        return f"Error retrieving sample data: {e}"
    
def get_database_info(conn):
    """Return detailed information about the database, including table schema and sample data."""
    table_info = []
    for table_name in get_table_names(conn):
        column_details = get_column_details(table_name)
        sample_data = get_table_sample_data(table_name)
        table_info.append({
            "table_name": table_name,
            "column_names": column_details,
            "sample_data": sample_data
        })
    return table_info



database_scheme_dict = get_database_info(connection)
database_schema_string = "\n".join(
    [
        f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}\nSample Data: {table['sample_data']}"
        for table in database_scheme_dict
    ]
)



def ask_database(query):
    """Function to query SQLite database with a provided SQL query."""
    try:
        results = str(connection.execute(query).fetchall())
        connection.commit()
        connection.close()
    except Exception as e:
        results = f"query failed with error: {e}"
    return results

def execute_function_call(message):
    if message.tool_calls[0].function.name == "ask_database":
        query = json.loads(message.tool_calls[0].function.arguments)["query"]
        results = ask_database(query)
        print(query, "results")
    else:
        results = f"Error: function {message.tool_calls[0].function.name} does not exist"
    return results



tools = [
    {
        "type": "function",
        "function": {
            "name": "ask_database",
            "description": "Gebruik deze functie om de Offerte database te bevragen met een SQL-query. De query moet in platte tekst worden geretourneerd, niet in JSON. De query mag ook GEEN rekenwerk bevatten! Er mogen geen prijzen ingesteld worden dit gebeurt achteraf automatisch, Als er iets aan de offerte moet worden toegevoegd mag je alleen dat doen en geen berekeningen uitvoeren",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"""
                                SQL query extracting info to answer the user's question.
                                SQL moet geschreven worden volgens dit database schema:
                                {database_schema_string}
                                The query should be returned in plain text, not in JSON.
                                HET IS OOK HEEL BELANGRIJK DAT JE CHECKT OF WAT ER GEVRAAGD WORDT MOGELIJK IS, BIJVOORBEELD, ALS ER BIJ EEN OFFERTE MET HET MATERIAALSOORT TAURUS TERRAZO WHITE VERZOET WORDT GEVRAAGD, MAG HET NIET ZO ZIJN DAT ER BOORGATEN TOEGEVOEGD KUNNEN WORDEN AAN DE OFFERTE! TEN ALLE TIJDEN NIET!, GEEF DAN ALS INPUT DAT HET NIET MOGELIJK IS OM BOORGATEN TOE TE VOEGEN AAN DE OFFERTE.
                                ALS EEN VRAAG GAAT OVER EEN MATERIAALSOORT MOET JE MEESTAL KIJKEN IN DE TABLE bladmatrix, ALS DE VRAAG GAAT OVER EEN OFFERTE MOET JE MEESTAL KIJKEN IN DE TABLE OFFERTE.
                                Als de offerte tabel moet veranderen gebruik dan alleen de UPDATE statement en gebruik nooit de INSERT, er mag maar 1 ROW blijven ten alle tijden in de offerte tabel.
                                Als je op WCD(wandcontactdoos) moet zoeken, noteer het dan op deze manier: "WCD_(Wandcontactdoos)", anders werkt het niet
                                JE HOEFT NOOIT ZELF EEN PRIJS IN TE VOEREN IN DE OFFERTE, DIT WORDT AUTOMATISCH GEDAAN, DUS BETREK DIT NOOOOIT IN JE SQL STATEMENT. Dus nooit een query maken voor de offerte_prijs waar je zelf een prijs invoert.
                                ZET OOK ALLLEEE KOLOM NAMEN TUSSEN APOSTROFEN, DUS 'kolomnaam' NIET kolomnaam

                                """,
                    }
                },
                "required": ["query"],
            },
        }
    }
]


def chat_completion_request(messages, tools):
    """Function to send a chat completion request to the OpenAI API."""
    chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-4-turbo-preview",
            tools= tools,
        )
    return chat_completion

# print(database_schema_string)
messages = []
messages.append({"role": "system", "content": f"Beantwoord de vragen door het creëren van een sql query, Die verwijst naar het volgende database schema:\n{database_schema_string}"})
prompt = input("Vraag iets: ")
messages.append({"role": "user", "content": f"{prompt}"})
chat_response = chat_completion_request(messages, tools)
assistant_message = chat_response.choices[0].message
assistant_message.content = str(assistant_message.tool_calls[0].function)
messages.append({"role": assistant_message.role, "content": assistant_message.content})
if assistant_message.tool_calls:
    results = execute_function_call(assistant_message)
    messages.append({"role": "function", "tool_call_id": assistant_message.tool_calls[0].id, "name": assistant_message.tool_calls[0].function.name, "content": results})
    print(results)



# print(database_schema_string)