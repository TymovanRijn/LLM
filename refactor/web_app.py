from flask import Flask, session, request, jsonify, render_template, abort, send_file, g
#from flask_cors import CORS
import uuid
import sqlite3
import shutil
import os
from pathlib import Path

from lmm_session import LMMSession
from openai import OpenAI
client = OpenAI(api_key=os.environ["API_KEY"])


app = Flask(__name__, template_folder="../templates", static_folder="../static")
#CORS(app)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# import logging

# logging.basicConfig(level=logging.DEBUG)
from fpdf import FPDF
def fetch_data():
    # db_path = f"./refactor/data/{session.get('uuid')}.sql" if session.get('uuid') else 'default.db'
    # print(f"Dit is de locatie: {db_path}")
    conn = get_lmm_instance().db_connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM offerte_prijs WHERE ID=1")
    data = cursor.fetchall()
    conn.close()
    return data


from pdf import PDF
def create_pdf(data):
    pdf = PDF()
    pdf.add_page()

    headers = ["Materiaalsoort", "Prijs Materiaalsoort", "Randafwerking", "Prijs Randafwerking", "Spatrand", "Prijs Spatrand", "Vensterbank", "Prijs Vensterbank", "Zeepdispenser", "Prijs Zeepdispenser", "Boorgaten", "Prijs Boorgaten", "WCD", "Prijs WCD", "Achterwand", "Prijs Achterwand", "m2"]

    if data:
        for row in data:
            pdf.chapter_title(f"Offerte ID: {row[0]}")
            for i, item in enumerate(row[1:]):  # Skip ID
                pdf.table_row(headers[i], item if item is not None else 'N/A')
            pdf.ln(10)

    filename = f"offerte-{session.get('uuid')}.pdf"
    output_dir = "./offertes"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pdf.output(os.path.join(output_dir, filename))

@app.route('/download-pdf')
def download_pdf():
    data = fetch_data()
    create_pdf(data)
    filename = f"offerte-{session.get('uuid')}.pdf"
    return send_file(f'./offertes/{filename}', as_attachment=True)

def get_db_conn(uuid_: str) -> sqlite3.Connection:
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    path = os.path.join(data_dir, f"{uuid_}.sql")
    src_path = "data/Offerte.sql"  # Ensure this is the correct path

    if not os.path.exists(data_dir):
        # logging.debug(f"Data directory not found at {data_dir}, creating directory.")
        os.makedirs(data_dir)

    if not os.path.exists(path):
        # logging.debug(f"Database file not found at {path}, attempting to copy from template.")
        if os.path.exists(src_path):
            shutil.copyfile(src_path, path)
            # logging.info(f"Database template copied from {src_path} to {path}.")
        else:
            # logging.error(f"Template database file not found at {src_path}")
            raise FileNotFoundError(f"Template database file not found at {src_path}")

    return sqlite3.connect(path)


@app.teardown_appcontext
def teardown_db(exception):
    db_conn = g.pop("db_conn", None)
    if db_conn is not None:
        db_conn.close()


def get_lmm_instance():
    uuid_ = session.get('uuid')
    if uuid_ is None:
        session["uuid"] = uuid.uuid4()
    db_conn = get_db_conn(uuid_)
    return LMMSession(os.environ["API_KEY"], db_conn)


@app.route('/get_offerte_data')
def get_offerte_data():
    lmm = get_lmm_instance()
    db_conn = lmm.db_connection
    try:
        db_conn.row_factory = sqlite3.Row
        cur = db_conn.cursor()
        cur.execute('SELECT * FROM offerte_prijs WHERE ID=1')
        offerte_items = cur.fetchall()
    finally:
        db_conn.row_factory = None

    return jsonify([dict(ix) for ix in offerte_items])

@app.route('/start_session', methods=['POST'])
def start_session():
    session_id = str(uuid.uuid4())
    session['id'] = session_id
    return jsonify({'session_id': session_id})

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'id' not in session:
        return jsonify({'error': 'Session not started'}), 400

    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio = request.files['audio']
    session_id = session['id']
    audio_filename = f"{session_id}_{uuid.uuid4()}.mp3"
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
    audio.save(audio_path)

    try:
        transcription = transcribe_audio(audio_path)
        return jsonify({'text': transcription})
    except Exception as e:
        # Log the exception to the server console
        print(f"Error during transcription: {e}")
        return jsonify({'error': 'An error occurred during transcription.'}), 500


def transcribe_audio(audio_path):
    try:
        with open(audio_path, 'rb') as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="json",
                language="nl"
            )

        # Log the full response for debugging
        print(f"Transcription service response: {response}")

        # Check if the response has the 'text' attribute
        if hasattr(response, 'text'):
            transcription = response.text
        else:
            raise TypeError(f"Unexpected response format from transcription service: {response}")

        # Delete the audio file after transcription
        os.remove(audio_path)
        print(f"Deleted audio file: {audio_path}")

        return transcription
    except Exception as e:
        # Log the exception to the server console
        print(f"Error in transcribe_audio function: {e}")
        raise e

@app.route('/generate_speech', methods=['POST'])
def generate_speech():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Generate a unique filename for the output file
    filename = f"{uuid.uuid4()}.mp3"
    static_dir = os.path.join(os.getcwd(), 'static')
    audio_file_path = os.path.join(static_dir, filename)

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
        )

        # Check if the response is received correctly
        print("Response received:", response)
        print("Response content type:", type(response.content))
        print("Response content length:", len(response.content))

        # Write the response content to a file
        with open(audio_file_path, 'wb') as audio_file:
            audio_file.write(response.content)
            print(f"Audio content written to {audio_file_path}")

        return jsonify({'filename': filename})

    except Exception as e:
        print(f"Error generating speech: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/delete_audio/<filename>', methods=['DELETE'])
def delete_audio(filename):
    static_dir = os.path.join(os.getcwd(), 'static')
    file_path = os.path.join(static_dir, filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': f'{filename} deleted successfully.'}), 200
        else:
            return jsonify({'error': 'File not found.'}), 404
    except Exception as e:
        print(f"Error deleting file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/send_message', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    if message is None:
        abort(400, "message missing")
    lmm = get_lmm_instance()
    response = lmm.prompt(message)
    return jsonify({'response': response})


@app.route('/')
def home():
    if session.get('uuid') is None:
        session["uuid"] = uuid.uuid4()
    return render_template("index.html")


if __name__ == '__main__':
    app.run(port=5000)
