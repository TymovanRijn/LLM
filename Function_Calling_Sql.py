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


def get_column_names(table_name):
    """Return a list of column names."""
    column_names = []
    columns = connection.execute(f"PRAGMA table_info('{table_name}');").fetchall()
    for col in columns:
        column_names.append(col[1])
    return column_names


def get_database_info(conn):
    """Return a list of dicts containing the table name and columns for each table in the database."""
    table_dicts = []
    for table_name in get_table_names(conn):
        columns_names = get_column_names(table_name)
        table_dicts.append({"table_name": table_name, "column_names": columns_names})
    return table_dicts



database_scheme_dict = get_database_info(connection)
database_schema_string = "\n".join(
    [
        f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}"
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
            "description": "Gebruik deze functie om de Offerte database te bevragen met een SQL-query. De query moet in platte tekst worden geretourneerd, niet in JSON.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"""
                                SQL query extracting info to answer the user's question.
                                SQL should be written using this database schema:
                                {database_schema_string}
                                The query should be returned in plain text, not in JSON.
                                HET IS OOK HEEL BELANGRIJK DAT JE CHECKT OF WAT ER GEVRAAGD WORDT MOGELIJK IS, BIJVOORBEELD, ALS ER BIJ EEN OFFERTE MET HET MATERIAALSOORT TAURUS TERRAZO WHITE VERZOET WORDT GEVRAAGD, MAG HET NIET ZO ZIJN DAT ER BOORGATEN TOEGEVOEGD KUNNEN WORDEN AAN DE OFFERTE! TEN ALLE TIJDEN NIET!, GEEF DAN ALS INPUT DAT HET NIET MOGELIJK IS OM BOORGATEN TOE TE VOEGEN AAN DE OFFERTE.
                                Als de offerte tabel moet veranderen gebruik dan alleen de UPDATE statement en gebruik nooit de INSERT, er mag maar 1 ROW blijven ten alle tijden in de offerte tabel.
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

messages = []
messages.append({"role": "system", "content": f"Answer user questions by generating SQL queries against the Offerte Database, which has the following schema:\n{database_schema_string}"})
messages.append({"role": "user", "content": "Welke materiaalsoorten zijn er?"})
chat_response = chat_completion_request(messages, tools)
assistant_message = chat_response.choices[0].message
assistant_message.content = str(assistant_message.tool_calls[0].function)
messages.append({"role": assistant_message.role, "content": assistant_message.content})
if assistant_message.tool_calls:
    results = execute_function_call(assistant_message)
    messages.append({"role": "function", "tool_call_id": assistant_message.tool_calls[0].id, "name": assistant_message.tool_calls[0].function.name, "content": results})
    print(messages)
    print("---------------------------------")
    print(results)



# print(database_schema_string)