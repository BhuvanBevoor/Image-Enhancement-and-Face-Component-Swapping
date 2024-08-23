import subprocess
import threading
from urllib import response

from flask import Flask, request, redirect, url_for, render_template, session, jsonify
from werkzeug.utils import secure_filename
import os, time

app = Flask(__name__, static_folder="./static")
app.secret_key = '959916'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/swap')
def upload_form():
    return render_template('index.html')


@app.route("/process", methods=['POST'])
def process():
    source_file = request.files['sourceImage']
    destination_file = request.files.get('destinationImage')
    parts = request.form.get('part')

    if source_file and allowed_file(source_file.filename):
        source_filename = secure_filename(source_file.filename)
        newname = "src." + source_filename.split('.')[-1]
        source_file.save(f'images_test/{newname}')

    if destination_file and allowed_file(destination_file.filename):
        destination_filename = secure_filename(destination_file.filename)
        newname2 = "dst." + destination_filename.split('.')[-1]
        destination_file.save(f'images_test/{newname2}')

    with open("output.txt", "w") as f:
        f.write("")
    lock = threading.Lock()

    def run_script():
        with lock:
            subprocess.run(['python', 'main_c.py', '--part', parts], stdout=open("output.txt", "w"))

    thread = threading.Thread(target=run_script)
    thread.start()
    return render_template("process.html")


@app.route("/process", methods=['GET'])
def process_refresh():
    time.sleep(5)
    with open("output.txt", "r") as f:
        output_text = f.read()
    return jsonify({'output': output_text})


@app.route("/result")
def final():
    return render_template("Final.html")


if __name__ == "__main__":
    app.run(debug=True)
