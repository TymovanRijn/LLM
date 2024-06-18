import sqlite3
import json
from openai import OpenAI




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







def ask_database(query):
    """Function to query SQLite database with a provided SQL query."""
    if "DELETE" in query.upper():
        return "Error: DELETE operation is not allowed"
    try:
        connection = sqlite3.connect('./data/Offerte.sql')
        cursor = connection.cursor()
        results = str(cursor.execute(query).fetchall())
        connection.commit()
    except Exception as e:
        results = f"query failed with error: {e}"
    finally:
        if connection:
            connection.close()
    return results

def execute_function_call(message):
    
    # print("EXECUTE FUNCTION CALL: " + message.tool_calls[0].message.content)
    if message.tool_calls[0].function.name == "add_to_offerte_table":
        query = json.loads(message.tool_calls[0].function.arguments)["query"]
        print("DIT IS DE QUERY: " + query)
        query_check = check_query(query)
        print("DIT IS DE CHECK: " + query_check)
        if "JA" in query_check.upper():
            results = ask_database(query)
        else:
            results = "Helaas is deze wijziging niet mogelijk."

        print(results)
        # print(query, "results")
    else:
        results = f"Error: function {message.tool_calls[0].function.name} does not exist"
    return results

def get_materiaalsoort():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT Materiaalsoort FROM offerte_prijs WHERE ID=1')  # Update de query indien nodig
    materiaalsoort = cur.fetchall()
    conn.close()
    return materiaalsoort

def check_query(query):
    materiaalsoort = get_materiaalsoort()
    print (materiaalsoort[0])
    materiaalsoort = materiaalsoort[0]
    messages = []
    messages.append({"role": "system", "content": f"""Als er een prijs van iets benoemd
                      wordt (op de offerte_prijs na) bijvoorbeeld van randafwerking o.i
                     .d in deze SQL query ({query}) op de offerte_prijs na, 
                     geef dan een nieuwe QUERY terug zonder dat die prijs wordt 
                     aangepast, HEEL BELANGRIJK! bij voorbeeld deze query:
                     UPDATE offerte_prijs SET Boorgaten = '10', Prijs_Boorgaten = 67.5 * 2 WHERE ID = 1;
                     zou niet mogen, omdat Prijs_Boorgaten wordt aangepast.
                      Dit is de query die je moet beoordelen: {query}
                        Wanneer de nieuwe prijs op NULL wordt gezet van iets dan is het wel
                      een geldige query en mag die dus behouden worden, anders niet!
                        GEEF ALLEEN DE NIEUWE QUERY ALS ANTWOORD NIKS ANDERS!
                       ALS ER GEEN PRIJS WORDT GENOEMD BEHOUDT DAN DE ORIGINELE QUERY 
                       EN GEEF ALLEEEN DIE TERUG!!"""})
    chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-4-turbo",
        )
    
    print("CHECK 0: " + chat_completion.choices[0].message.content)
    if "JA" in chat_completion.choices[0].message.content.upper():
        query = query
    else:
        query = chat_completion.choices[0].message.content

    messages = []
    if "SET MATERIAALSOORT" not in query.upper() or "SET 'MATERIAALSOORT'" not in query.upper() or "SET M2" not in query.upper() or "SET 'M2'" not in query.upper() :

        
        # messages.append({"role": "system", "content": f"""Check"""})
        # chat_completion = client.chat.completions.create(
        #     messages=messages,
        #     model="gpt-4-turbo-preview",
        # )
        # result = chat_completion.choices[0].message.content
        pass
    else:
        result = "JA"
    return result

def get_db_connection():
    return sqlite3.connect('./data/Offerte.sql', check_same_thread=False)

connection = get_db_connection()

global database_schema_string
database_schema_string = ""

def update_database_schema_string():
    global database_schema_string
    database_scheme_dict = get_database_info(connection)
    database_schema_string = "\n".join(
        [
            f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}\nSample Data: {table['sample_data']}"
            for table in database_scheme_dict
        ]
    )
    return database_schema_string

def chat_completion_request(messages, tools):
    
    
    materiaalsoort = get_materiaalsoort()[0]
    
    """Function to send a chat completion request to the OpenAI API."""
    messages.append({"role": "system", "content": f"Beantwoord de vragen aan de hand van de informatie uit de de excel/database:\n{database_info}. \
                         Momenteel is de gekozen materiaal soort {materiaalsoort} Je mag alleen SQL Queries gebruiken om producten toe te voegen aan de offerte, anders mag dit ten alle tijden NIET! En moet je dus gewoon op basis van de info je antwoord geven."})
    chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-4-turbo",
            tools= tools,
        )
    return chat_completion


global database_info
def excel_info(excel_path):
    import pandas as pd
    global database_info
    # Laden van de 'Bladenmatrix' sheet
    bladenmatrix_df = pd.read_excel(excel_path, sheet_name="Bladenmatrix", header=0)
    
    # Correct instellen van de headers
    nieuwe_headers = bladenmatrix_df.iloc[0]  # De eerste rij bevat de juiste headers
    bladenmatrix_df = bladenmatrix_df[1:]  # Verwijder de eerste rij met de oude headers
    bladenmatrix_df.columns = nieuwe_headers  # Stel de nieuwe headers in
    
    # Omvormen van DataFrame naar een dictionary
    bladenmatrix_dict = {}
    for index, row in bladenmatrix_df.iterrows():
        materiaalsoort = row['Materiaalsoort']
        materiaal_info = {col: row[col] for col in bladenmatrix_df.columns if col != 'Materiaalsoort'}
        bladenmatrix_dict[materiaalsoort] = materiaal_info
    
    # Zet alle informatie in de database_info string
    database_info = ""
    for materiaalsoort, info in bladenmatrix_dict.items():
        database_info += f"\n\nMateriaalsoort: {materiaalsoort}\n"
        for key, value in info.items():
            # Controleer of de waarde numeriek is en niet eindigt op 'mm'
            if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit() and not value.lower().endswith('mm')):
                value = f"{value} euro"  # Voeg ' euro' toe aan de waarde
            elif isinstance(value, str) and not value.lower().endswith('mm'):
                # Voor het geval dat de waarde een string is die een getal bevat maar niet eindigt op 'mm'
                try:
                    float_value = float(value.replace(',', '.'))
                    value = f"{value} euro"
                except ValueError:
                    pass  # Niet aangepast als het niet omgezet kan worden naar een getal
            database_info += f"{key}: {value}\n"

    return bladenmatrix_dict



            
        




# print(database_schema_string)
