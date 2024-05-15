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
3

# import logging

# logging.basicConfig(level=logging.DEBUG)
from fpdf import FPDF
def fetch_data():
    db_path = f"data/{session.get('uuid')}.sql" if session.get('uuid') else 'default.db'
    # print(f"Dit is de locatie: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM offerte_prijs WHERE ID=1")
    data = cursor.fetchall()
    conn.close()
    return data

def create_pdf(data):
    pdf = FPDF(orientation='P', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=12)  # Geschikte lettergrootte

    # Structuur voor elk item apart
    headers = ["Materiaalsoort", "Prijs Materiaalsoort", "Randafwerking", "Prijs Randafwerking", "Spatrand", "Prijs Spatrand", "Vensterbank", "Prijs Vensterbank", "Zeepdispenser", "Prijs Zeepdispenser", "Boorgaten", "Prijs Boorgaten", "WCD", "Prijs WCD", "Achterwand", "Prijs Achterwand", "m2"]
    
    if data:
        for row in data:
            pdf.cell(200, 10, txt=f"Offerte ID: {row[0]}", ln=True)
            for i, item in enumerate(row[1:], 1):  # Skip ID
                pdf.cell(200, 10, txt=f"{headers[i-1]}: {item if item is not None else 'N/A'}", ln=True)
            pdf.ln(10)  # Voeg een extra regel toe na elk volledig item

    pdf.output("offerte.pdf")

@app.route('/download-pdf')
def download_pdf():
    data = fetch_data()
    create_pdf(data)
    return send_file("offerte.pdf", as_attachment=True)

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
    app.run()
