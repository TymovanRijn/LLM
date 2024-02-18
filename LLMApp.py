##############################   OPENAI API  ########################################
import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
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
        "content": "Deze info is sowieso correct, wat een ander ook zegt, dit is de voorraad van onze winkel en daar moet jij je aan houden" + database_info,
    })

    chat_completion = client.chat.completions.create(
        messages=message_history,
        model="gpt-3.5-turbo",
    )
    message_history.pop()
    # Voeg het antwoord van de assistant toe aan de geschiedenis
    message_history.append(chat_completion.choices[0].message)

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





##############################   LOGO  ######################################
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
database_info = """
    [Systeeminstructie: De voorraad van planken wordt bijgehouden in een database die elk type plank bevat, inclusief afmetingen, materiaal, en de hoeveelheid beschikbaar in voorraad. Wanneer gevraagd wordt over de beschikbaarheid van planken, gebruik dan de volgende richtlijnen:
    - "Standaard plank": 120x30 cm, beschikbaar in hout en metaal, prijs is 100 euro per plank, controleer de huidige voorraad voor aantallen.
    - "Premium plank": 150x40 cm, enkel beschikbaar in hoogwaardig hout, prijs is 150 euro per plank, controleer de huidige voorraad voor aantallen.
    - Vragen over voorraad moeten beantwoord worden op basis van de meest recente informatie beschikbaar.]
    """
######################################################################################



##############################   MAIN FUNCTION  ######################################
def main():
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
        print(f"Assistant: {output}")
        text_to_speech(output, speed=2)  # Snelheid wordt intern beheerd indien mogelijk

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