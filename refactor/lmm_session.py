from typing import Any


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


    def __init__(self, api_key: str, db_connection) -> None:
        self._api_key = api_key
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
            sample_data = connection.execute(f"SELECT * FROM {table_name} LIMIT {limit};").fetchall()
            return sample_data
        except Exception as e:
            return f"Error retrieving sample data: {e}"

    def _gen_database_schema_string(self) -> str:
        database_schema_dict = self._get_database_info()
        database_schema_string = "\n".join((
            f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}\nSample Data: {table['sample_data']}"
            for table in database_schema_dict
        ))

    def _append_message(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})

    def _append_system_guideline_message(self, messages: list):
        database_schema_string = self._gen_database_schema_string()
        messages.append({
            "role": "system",
            "content": f"Beantwoord de vragen Super netjes en beleefd. Je werkt bij BlisDigital. Dit is de huidige Database van de offerte: \n{database_schema_string}\nJe mag alleen SQL Queries gebruiken om producten toe te voegen aan de offerte, anders mag dit ten alle tijden NIET! En moet je dus gewoon op basis van de info je antwoord geven. Als iets niet mogelijk is met een bepaalde materiaalsoort mag je dus ook ten alle tijden het niet mogelijk maken in de offerte."
        })
        return messages

    def generate_database_string():
        pass

    def get_offerte_data():
        pass

    def _request_chat_completion(self, messages: list) -> Any:
        materiaal_soort = self._get_materiaal_soort()
        database_info = gen
        messages.append(
            "system",
            f"Beantwoord de vragen aan de hand van de informatie uit de de excel/database:\n{database_info}. Momenteel is de gekozen materiaal soort {materiaalsoort} Je mag alleen SQL Queries gebruiken om producten toe te voegen aan de offerte, anders mag dit ten alle tijden NIET! En moet je dus gewoon op basis van de info je antwoord geven."
        )
        return self._create_completion(messages, self._tools)

    def _create_completion(self, messages: list, tools=None) -> Any:
        return client.chat.completions.create(
            messages=messages,
            model="gtp-4-turbo",
            tools=tools
        )

    def _get_materiaal_soort(self) -> str:
        return self._db_connection.execute(
            'SELECT Materiaalsoort FROM offerte_prijs WHERE ID=1'
        ).fetchone()

    def _execute_function_call(self, message):
        if message.tools_calls[0].function_name == "add_to_offerte_table":
            query = json.loads(message.tool_calls[0].function.arguments)["query"]
            query_check = check_query(query)
            if "JA" in query_check.upper():
                results = self._try_query_database(query)
            else:
                results = "Helaas is deze wijziging niet mogelijk."
        else:
            results = f"Error: function {message.tool_calls[0].function.name} does not exist"
        return results

    def _try_query_database(self, query):
        if not self._check_sql_query(query):
            return "Error: DELETE operation is not allowed"
        cursor = self._db_connection.cursor()
        results = str(cursor.execute(query).fetchall())
        return results

    @staticmethod
    def _check_sql_query(query: str) -> bool:
        return "DELETE" in query.upper()

    def _check_query(self, query) -> None:
        materiaal_soort = self._get_materiaal_soort()
        messages = _Messages()
        messages.append(
            "system",
            f"""Als er een prijs van iets benoemd
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
                       EN GEEF ALLEEEN DIE TERUG!!"""
        )
        chat_completion = self._create_completion(messages.messages)
        if "JA" not in chat_completion.choices[0].message.content.upper():
            query = chat_completion.choices[0].message.content.upper();

        messages = Messages()
        if (
            "SET MATERIAALSOORT" not in query.upper()
            and "SET MATERIAALSOORT" not in query.upper()
            and "SET 'M2'" not in query.upper()
            and "SET M2" not in query.upper()
        ):
            messages.append(
                "system",
                f"""Je moet kijken of de gekozen materiaalsoort ({materiaalsoort} de actie die wordt genoemd in de query ({query}) mogelijk is. Dus bijvoorbeeld Set boorgaten, hiervoor moet je eerst
                         goed kijken of de boorgaten wel mogelijk zijn bij deze materiaalsoort, dit kun je hier checken: {database_info}. ALS de uitvoering mogelijk is, geef dan het antwoord 'JA' terug, anders 'NEE'."""
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
        # Try to call a function if the LMM asks to
        if assistant_message.tool_calls:
            self._execute_function_call(assistant_message)
            self._messages.append(
                {"role": "function", "tool_call_id": assistant_message.tool_calls[0].id, "name": assistant_message.tool_calls[0].function.name, "content": results}
            )
            if "HELAAS IS DEZE WIJZIGING NIET MOGELIJK" in results.upper():
                response_content = "Helaas is deze wijziging niet mogelijk."
            else:
                response_content = "Succesvol uitgevoerd!"
        # Just return the LMM's response to the user
        else:
            response_content = chat_completion_choices[0].messages.content
        return response_content

