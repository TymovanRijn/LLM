import os
from openai import OpenAI
import time
start_time = time.time()
client = OpenAI(
    api_key= "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",	
)

message_history = []

def prompt(content, database_info):
    global message_history  # Verwijs naar de globale variabele

    # Voeg de nieuwe gebruikersinvoer toe aan de geschiedenis
    message_history.append({
        "role": "user",
        "content": content,
    })
    message_history.append({
        "role": "system",
        "content": "De volgende informatie reflecteert de actuele voorraadstatus \
            van onze winkel en dient als de primaire bron voor voorraadinformatie. \
                Gelieve deze gegevens te gebruiken als basis voor alle antwoorden gerelateerd aan voorraadvragen." + database_info,
    })

    chat_completion = client.chat.completions.create(
        messages=message_history,
        model="gpt-3.5-turbo",
    )
    message_history.pop()
    # Voeg het antwoord van de assistant toe aan de geschiedenis
    message_history.append(chat_completion.choices[0].message)

    return chat_completion.choices[0].message.content

if __name__ == "__main__":
    print("Why are banana's straight?")
    print(prompt("Why are banana's straight?", "Bananen: 100 stuks"))
    elapsed_time = time.time() - start_time
    print("Totale uitvoertijd: ", elapsed_time, " seconden.")