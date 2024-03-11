##############################   OPENAI API  ########################################
import os
from openai import OpenAI
import pandas as pd
import time
import json
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

    if "maak een offerte" in content.lower():
        chat_completion = client.chat.completions.create(
            messages=message_history,
            model="gpt-3.5-turbo",
            tools= tools,
        )
    else:
        chat_completion = client.chat.completions.create(
            messages=message_history,
            model="gpt-3.5-turbo",
        )
    message_history.pop()
    # Voeg het antwoord van de assistant toe aan de geschiedenis
    message_history.append(chat_completion.choices[0].message)
    time.sleep(1.5)
    
    if chat_completion.choices[0].message.tool_calls is not None:
        for tool_call in chat_completion.choices[0].message.tool_calls:
            print(chat_completion.choices[0].message.tool_calls[0].function.arguments)
            parameters_json = chat_completion.choices[0].message.tool_calls[0].function.arguments
            parameters = json.loads(parameters_json)
        
            # Roep je functie aan met de geëxtraheerde parameters
            resultaat = Voeg_item_toe(**parameters)  # De ** operator wordt gebruikt om de dictionary te unpacken als keyword arguments
            # Voeg een responsbericht toe voor de tool call
            message_history.append({
                "role": "function",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": resultaat  # Dit moet het resultaat van je tool call simulatie zijn
            })
    else:
        print("No tool calls")

    return chat_completion.choices[0].message.content


#####################################################################################


##############################   SPEECH RECOGNITION  ################################
import speech_recognition as sr

r = sr.Recognizer()

def record_audio():
    with sr.Microphone() as source:
        print("Wat wilt u vragen?")
        audio = r.listen(source)
        print("Uw vraag wordt verwerkt")
    return audio

def speech_to_text(audio):
    try:
        text = r.recognize_google(audio, language='nl-NL')
        return text
    except:
        return "Sorry, wilt u dat herhalen?"
#####################################################################################




##############################   TEXT TO SPEECH  ######################################
import os
import pygame
from gtts import gTTS
# from pydub import AudioSegment

def text_to_speech(text, speed=2):
    # Initialiseer pygame mixer
    pygame.mixer.init()
    
    # Gebruik gTTS om de tekst om te zetten naar spraak en sla het op als een MP3
    tts = gTTS(text=text, lang='nl')
    filename = "output.mp3"
    tts.save(filename)
    
    # Als je kiest voor een methode om de snelheid aan te passen, zou je hier pydub kunnen gebruiken
    # sound = AudioSegment.from_mp3(filename)
    # sound_with_adjusted_speed = sound.speedup(playback_speed=speed)
    # adjusted_filename = "adjusted_output.mp3"
    # sound_with_adjusted_speed.export(adjusted_filename, format="mp3")
    # filename = adjusted_filename  # Zorg ervoor dat pygame het aangepaste bestand laadt

    # Laad het geluidsbestand en speel het af
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    
    # Wacht tot het afspelen klaar is
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()  # Zorg ervoor dat het bestand is losgelaten
    pygame.mixer.quit()  # Afsluiten van de mixer
    
    # Opruimen: verwijder het tijdelijke bestand
    os.remove(filename)


#####################################################################################





#########################################  LOGO  ############################################
def logo():
    print(" ________  ___       ___  ________  ________  ___  ________  ___  _________  ________  ___          ")
    print("|\   __  \|\  \     |\  \|\   ____\|\   ___ \|\  \|\   ____\|\  \|\___   ___\\   __  \|\  \         ")
    print("\ \  \|\ /\ \  \    \ \  \ \  \___|\ \  \_|\ \ \  \ \  \___|\ \  \|___ \  \_\ \  \|\  \ \  \        ")
    print(" \ \   __  \ \  \    \ \  \ \_____  \ \  \ \\ \ \  \ \  \  __\ \  \   \ \  \ \ \   __  \ \  \       ")
    print("  \ \  \|\  \ \  \____\ \  \|____|\  \ \  \_\\ \ \  \ \  \|\  \ \  \   \ \  \ \ \  \ \  \ \  \____  ")
    print("   \ \_______\ \_______\ \__\____\_\  \ \_______\ \__\ \_______\ \__\   \ \__\ \ \__\ \__\ \_______\ ")
    print("    \|_______|\|_______|\|__|\_________\|_______|\|__|\|_______|\|__|    \|__|  \|__|\|__|\|_______|")
    print("                            \|_________|                                                            ")
####################################################################################################



##############################   DATABASE INFO  ######################################
global database_info



def excel_info(excel_path):
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




######################################################################################


##############################   OFFERTE MAKEN  ######################################
tools = [
    {
 "type": "function",
        "function": {
            "name": "Voeg_item_toe",
            "description": "Voegt een item toe aan de huidige offerte, alleen als er wordt gevraagd: Maak een offerte.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Materiaalsoort": {
                        "type": "string",
                        "enum": ["Noble Desiree Grey Matt", "noble Carrara Verzoet", "Taurus terazzo White Verzoet", "Tarus Terazzo Black", "Glencoe Verzoet"],
                        "description": "Het matereriaalsoort van het item, deze moet verkregen worden door de gebruiker en gecheckt worden of het mogelijk is.",
                    },
                    "Spatrand": {
                        "type": "integer",
                        "description": "De lengte van de spatrand, deze moet door de gebruiker gegeven worden en worden gecheckt of het mogelijk is.",
                    },
                    "Vensterbank": {
                        "type": "integer",
                        "description": "De lengte van de vensterbank, deze moet door de gebruiker gegeven worden en worden gecheckt of het mogelijk is.",
                    },
                    "Boorgaten": {
                        "type": "integer",
                        "description": "Het aantal boorgaten, deze moet door de gebruiker gegeven worden en worden gecheckt of het mogelijk is.",
                    },
                    "Wandcontactdoos": {
                        "type": "boolean",
                        "description": "Of er een wandcontactdoos aanwezig moet zijn, check wel zelf eerst of dit mogelijk is.",
                    },
                    "Randafwerking": {
                        "type": "boolean",
                        "description": "De randafwerking van het item, check wel zelf eerst of dit mogelijk is.",
                    },
                    "Aantal_Vierkante_Meter": {
                        "type": "integer",
                        "description": "Het aantal vierkante meter dat men wilt hebben, check wel zelf eerst of dit mogelijk is.",
                    },
                

                },
                "required": ["Materiaalsoort", "Spatrand", "Vensterbank", "Boorgaten", "Wandcontactdoos", "Randafwerking", "Aantal_Vierkante_Meter"],
            },
        }
    },
    
]

def Voeg_item_toe(Materiaalsoort, Spatrand, Vensterbank, Boorgaten, Wandcontactdoos, Randafwerking, Aantal_Vierkante_Meter):
    global database_info
    # Laden van de 'Bladenmatrix' sheet
    print(f"Materiaalsoort: {Materiaalsoort}\n Spatrand: {Spatrand}\n Vensterbank: {Vensterbank}\n Boorgaten: {Boorgaten}\n Wandcontactdoos: {Wandcontactdoos}\n Randafwerking: {Randafwerking}\n Aantal_Vierkante_Meter: {Aantal_Vierkante_Meter}\n")


##############################   MAIN FUNCTIE  ######################################
def main():
    global database_info
    excel_info("Bladenmatrix.xlsx")
    print(database_info)
    message_count = 0  # Teller om het aantal berichten bij te houden
    while True:
        # Clear het scherm en toon het logo na elke vier berichten
        if message_count % 2 == 0:
            clear_console()
            logo()
            print("Type 'quit' om te stoppen of zeg 'stop' tijdens de audio-opname.\n")

        # Record audio en converteer naar tekst
        print("\nDruk op Enter om te beginnen met opnemen...")
        input()
        audio = record_audio()
        user_input = speech_to_text(audio)
        print(f"Jij: {user_input}")

        # Check voor stopwoord of commando om af te sluiten
        if "stop" in user_input.lower() or user_input.lower() == "quit":
            break

        # Verkrijg en toon response
        output = prompt(user_input, database_info)
        if output is None or output == "":
            pass
        else:
            print(f"Assistant: {output}")
            text_to_speech(output)  # Snelheid wordt intern beheerd indien mogelijk
        

        # Wacht op Enter om door te gaan
        message_count += 1

#########################################################################################


##############################   OVERIGE FUNCTIES  ######################################
def clear_console():
    # Voor Windows
    if os.name == 'nt':
        os.system('cls')
    # Voor macOS en Linux (os.name is 'posix' hier)
    else:
        os.system('clear')
#########################################################################################




if __name__ == "__main__":
    main()