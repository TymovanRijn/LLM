from flask import Flask, session, request, jsonify, render_template
#from flask_cors import CORS
import uuid
import sqlite3
import shutil
import os

from lmm_session import LMMSession


app = Flask(__name__, template_folder="../templates", static_folder="../static")
#CORS(app)
app.secret_key = os.urandom(24)


lmm_sessions = {}


def new_user_session():
    uid = uuid.uuid4()
    session['uid'] = uid
    db_path = f"./data/{uid}.sql"
    shutil.copyfile("../data/Offerte.sql", db_path)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    lmm_sessions[uid] = LMMSession(os.environ["API_KEY"], conn)


def get_lmm_session():
    uid = session.get('uid')
    if uid is None:
        abort(400, "Uid is not in session")
    lmm_session = lmm_sessions.get(uid)
    if lmm_session is None:
        abort(500, "Internal server error")
    return lmm_session


@app.route('/get_offerte_data')
def get_offerte_data():
    lmm_session = get_lmm_sesion()
    conn = lmm_sesion.db_connection
    cur = conn.cursor()
    cur.execute('SELECT * FROM offerte_prijs WHERE ID=1')
    offerte_items = cur.fetchall()
    return jsonify((dict(ix) for ix in offerte_items))


@app.route('/send_message', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    if message is None:
        abort(400, "message missing")
    lmm_session = get_lmm_session()
    response = lmm_session.prompt(message)
    return jsonify({'response': response})


@app.route('/')
def home():
    if "uid" not in session:
        new_user_session()

    return render_template("index.html")


if __name__ == '__main__':
    app.run()
