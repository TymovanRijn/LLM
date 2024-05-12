from flask import Flask, session, request, jsonify, render_template, abort, g
#from flask_cors import CORS
import uuid
import sqlite3
import shutil
import os
from pathlib import Path

from lmm_session import LMMSession


app = Flask(__name__, template_folder="../templates", static_folder="../static")
#CORS(app)
app.secret_key = os.urandom(24)


# import logging

# logging.basicConfig(level=logging.DEBUG)


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
