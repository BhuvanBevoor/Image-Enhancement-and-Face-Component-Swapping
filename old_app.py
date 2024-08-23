import subprocess

from flask import Flask, request, redirect, url_for, render_template, session, jsonify, g
from werkzeug.utils import secure_filename
import os

app = Flask(__name__, static_folder="./static")
app.secret_key = '959916'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.after_request
def after_request(response):
    update_processing_output()
    return response


def update_processing_output():
    # Check if output file exists
    if os.path.isfile('output.txt'):
        # Read last modified time of output file
        last_modified = os.path.getmtime('output.txt')

        # Check if session has a stored timestamp
        if 'output_timestamp' not in session or session['output_timestamp'] != last_modified:
            # Update session with latest content and timestamp
            with open('output.txt', 'r') as f:
                processing_output = f.read()
            session['processing_output'] = processing_output
            session['output_timestamp'] = last_modified


@app.route('/', methods=['GET', 'POST'])
def mainpage():
    g.parts = 'face'
    return render_template('main.html')


@app.route('/swap', methods=['GET', 'POST'])
def upload_form():
    if request.method == 'POST':
        source_file = request.files['sourceImage']
        destination_file = request.files.get('destinationImage')
        g.parts = request.form.get('part')

        if source_file and allowed_file(source_file.filename):
            source_filename = secure_filename(source_file.filename)
            newname = "src." + source_filename.split('.')[-1]
            source_file.save(f'images_test/{newname}')

        if destination_file and allowed_file(destination_file.filename):
            destination_filename = secure_filename(destination_file.filename)
            newname2 = "dst." + destination_filename.split('.')[-1]
            destination_file.save(f'images_test/{newname2}')
        return redirect('process')
    return render_template('index.html')


@app.route('/get_session_output')
def get_session_output():
    output = session.get('processing_output', '')
    return jsonify({'output': output})


@app.route("/process")
def process():
    with open("output.txt", "w") as output_file:
        output_file.write("")
    subprocess.run(['python', 'main_c.py', '--part', g.parts])

    return render_template("process.html")


@app.route("/result")
def final():
    return render_template("Final.html")


if __name__ == "__main__":
    app.run(debug=True)
