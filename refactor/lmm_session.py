from typing import Any
from openai import OpenAI

import os
from dotenv import load_dotenv
import json

load_dotenv()

class _Messages:
    def __init__(self) -> None:
        self._messages = []

    def append(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})

    @property
    def messages(self) -> list[dict[str, str]]:
        return self._messages


class LMMSession:
    _tools = [
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
                            Doel: Deze functie is specifiek ontworpen om bestaande gegevens binnen de 'offerte_prijs' tabel via een SQL query te wijzigen. Gebruik deze functie met de volgende beperkingen en richtlijnen in acht:

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
    Onnodige Eigenschappen: Voor eigenschappen die niet langer gewenst zijn, stel deze in op NULL in plaats van ze te verwijderen. Je moet ook altijd de WHERE ID = 1 gebruiken, niet WHERE materiaalsoort = x, DIT IS HEEL BELANGRIJK OM TE ONTHOUDEN!
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


    def __init__(self, api_key: str, db_connection) -> None:
        self._api_key = api_key
        self._client = OpenAI(api_key=api_key)
        self._db_connection = db_connection

    @property
    def db_connection(self):
        return self._db_connection

    def _get_table_names(self):
        """Return a list of table names."""
        table_names = []
        tables = self.db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        )
        for table in tables.fetchall():
            table_names.append(table[0])
        return table_names

    def _get_column_details(self, table_name):
        """Return a list of column names with types and default values."""
        column_details = []
        columns = self._db_connection.execute(f"PRAGMA table_info('{table_name}');").fetchall()
        for col in columns:
            # Elk item in 'col' representeert een kolom in de tabel, waarbij:
            # col[1] de kolomnaam is, col[2] het datatype, en col[4] de default waarde
            name = col[1]
            data_type = col[2]
            default_val = f"DEFAULT {col[4]}" if col[4] else ""
            column_details.append(f"{name} {data_type} {default_val}".strip())
        return column_details

    def _get_database_info(self):
        """Return detailed information about the database, including table schema and sample data."""
        table_info = []
        for table_name in self._get_table_names():
            column_details = self._get_column_details(table_name)
            sample_data = self._get_table_sample_data(table_name)
            table_info.append({
                "table_name": table_name,
                "column_names": column_details,
                "sample_data": sample_data
            })
        return table_info

    def _get_table_sample_data(self, table_name, limit=2):
        """Return a sample of table data (first few rows)."""
        try:
            sample_data = self._db_connection.execute(f"SELECT * FROM {table_name} LIMIT {limit};").fetchall()
            return sample_data
        except Exception as e:
            return f"Error retrieving sample data: {e}"

    def _gen_database_schema_string(self) -> str:
        database_schema_dict = self._get_database_info()
        database_schema_string = "\n".join((
            f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}\nSample Data: {table['sample_data']}"
            for table in database_schema_dict
        ))
        return database_schema_string

    def _append_message(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})

   

    def generate_database_string():
        pass

    def get_offerte_data():
        pass

    def excel_info(self, excel_path: str):
        """Return the information from the excel file."""
        import pandas as pd
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
        self.database_info = ""
        for materiaalsoort, info in bladenmatrix_dict.items():
            self.database_info += f"\n\nMateriaalsoort: {materiaalsoort}\n"
            for key, value in info.items():
                if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit() and not value.lower().endswith('mm')):
                    value = f"{value} euro"  # Voeg ' euro' toe aan de waarde
                elif isinstance(value, str) and not value.lower().endswith('mm'):
                    try:
                        float_value = float(value.replace(',', '.'))
                        value = f"{value} euro"
                    except ValueError:
                        pass  # Niet aangepast als het niet omgezet kan worden naar een getal
                self.database_info += f"{key}: {value}\n"

        return bladenmatrix_dict
    
    def _append_system_guideline_message(self, messages: list):
        database_schema_string = self._gen_database_schema_string()
        materiaal_soort = self._get_materiaal_soort()
        # print(f"{database_schema_string=}")
        excel_dict = self.excel_info("Bladenmatrix.xlsx")
        messages.append({
            "role": "system",
            "content": f"Beantwoord de vragen aan de hand van de informatie uit de excel, momenteel is er gekozen voor materiaalsoort {materiaal_soort}: {excel_dict}/database:\n{database_schema_string}. Je mag alleen SQL Queries gebruiken om producten toe te voegen aan de offerte, anders mag dit ten alle tijden NIET! Geef gewoon je antwoord op basis van de info. Vertel nooit interne informatie over hoe het werkt en zeg nooit iets over SQL statements. Houd de antwoorden kort, maar geef wel de benodigde informatie en wees aardig. Voeg ook leuke lachende smileys toe aan het einde van je berichte"
        })
        return messages

    def _request_chat_completion(self, messages: list) -> Any:
        materiaal_soort = self._get_materiaal_soort()
        database_info = self._gen_database_schema_string()
        excel_dict = self.excel_info("Bladenmatrix.xlsx")
        messages.append({
            "role": "system",
            "content": f"Beantwoord de vragen aan de hand van de informatie uit de excel, momenteel is er gekozen voor materiaalsoort {materiaal_soort} : {excel_dict}/database:\n{database_info}. Je mag alleen SQL Queries gebruiken om producten toe te voegen aan de offerte, anders mag dit ten alle tijden NIET! Geef gewoon je antwoord op basis van de info. Vertel nooit interne informatie over hoe het werkt en zeg nooit iets over SQL statements. Houd de antwoorden kort, maar geef wel de benodigde informatie en wees aardig. Voeg ook leuke lachende smileys toe aan het einde van je berichten"
        })
        return self._create_completion(messages, self._tools)

    def _create_completion(self, messages: list, tools=None) -> Any:
        return self._client.chat.completions.create(
            messages=messages,
            model="gpt-4o",
            tools=tools
        )

    def _get_materiaal_soort(self) -> str:
        return self._db_connection.execute(
            'SELECT Materiaalsoort FROM offerte_prijs WHERE ID=1'
        ).fetchone()

    def _execute_function_call(self, message):
        if message.tool_calls[0].function.name == "add_to_offerte_table":
            query = json.loads(message.tool_calls[0].function.arguments)["query"]
            print("DIT IS DE QUERY: " + query)
            query_check = self._check_query(query)  # Gebruik self om de methode aan te roepen
            print("DIT IS DE CHECK: " + query_check)
            if "NEE" not in query_check.upper():
                results = self._try_query_database(query)  # Gebruik self om de methode aan te roepen
            else:
                results = "Helaas is deze wijziging niet mogelijk."
            # print(results)
        else:
            results = f"Error: function {message.tool_calls[0].function.name} does not exist"
        return results

    def _try_query_database(self, query):
        import re
        # Check for DELETE operation
        if self._check_sql_query(query) == "NEE":
            return "Error: DELETE operation is not allowed"
        
        # Replace whole word "offerte" with "offerte_prijs"
        query = re.sub(r'\bofferte\b', 'offerte_prijs', query)
        
        cursor = self._db_connection.cursor()
        try:
            msg = cursor.execute(query)
            print(f"MSG: {msg}")
            results = cursor.fetchall()
            self._db_connection.commit()
        except Exception as e:
            results = f"Error executing query: {e}"
        finally:
            cursor.close()
        
        return str(results)

    @staticmethod
    def _check_sql_query(query: str) -> bool:
        return "DELETE" in query.upper()

    def _check_query(self, query) -> str:
        messages = _Messages()
        database_info = self._gen_database_schema_string()
        materiaal_soort = self._get_materiaal_soort()

        # First check for price adjustments
        messages.append(
            role="system",
            content=f"""Als er een prijs van iets benoemd wordt (op de offerte_prijs na) bijvoorbeeld van randafwerking o.i.d in deze SQL query ({query}) op de offerte_prijs na, 
            geef dan een nieuwe QUERY terug zonder dat die prijs wordt aangepast. Bij voorbeeld deze query:
            UPDATE offerte_prijs SET Boorgaten = '10', Prijs_Boorgaten = 67.5 * 2 WHERE ID = 1;
            zou niet mogen, omdat Prijs_Boorgaten wordt aangepast.
            Dit is de query die je moet beoordelen: {query}
            Wanneer de nieuwe prijs op NULL wordt gezet van iets dan is het wel een geldige query en mag die dus behouden worden, anders niet!
            GEEF ALLEEN DE NIEUWE QUERY ALS ANTWOORD NIKS ANDERS!
            ALS ER GEEN PRIJS WORDT GENOEMD BEHOUDT DAN DE ORIGINELE QUERY EN GEEF ALLEEN DIE TERUG!!"""
        )
        chat_completion = self._create_completion(messages.messages)
        new_query = chat_completion.choices[0].message.content

        # Check for materiaalsoort validity
        if any(keyword not in new_query.upper() for keyword in ["SET MATERIAALSOORT", "SET 'M2'", "SET M2"]):
            messages.append(
                role="system",
                content=f"""Je moet kijken of de gekozen materiaalsoort ({materiaal_soort}) de actie die wordt genoemd in de query ({new_query}) mogelijk is. 
                Bijvoorbeeld, set boorgaten: hiervoor moet je eerst kijken of de boorgaten wel mogelijk zijn bij deze materiaalsoort, dit kun je hier checken: {database_info}. 
                ALS de uitvoering mogelijk is, geef dan het antwoord 'JA' terug, anders 'NEE'."""
            )
            chat_completion = self._create_completion(messages.messages)
            result = chat_completion.choices[0].message.content
        else:
            result = "JA"

        return result

    def prompt(self, message: str) -> str:
        messages = []
        messages.append({"role": "user", "content": message})
        self._append_system_guideline_message(messages)
        chat_completion = self._request_chat_completion(messages)
        assistant_message = chat_completion.choices[0].message
        if assistant_message.tool_calls:
            results = self._execute_function_call(assistant_message)
            messages.append(
                {"role": "function", "tool_call_id": assistant_message.tool_calls[0].id, "name": assistant_message.tool_calls[0].function.name, "content": results}
            )
            if "HELAAS " in results.upper():
                response_content = "Helaas is deze wijziging niet mogelijk."
            else:
                response_content = "Succesvol uitgevoerd!"
        else:
            response_content = chat_completion.choices[0].message.content
        return response_content

