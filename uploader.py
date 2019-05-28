from flask import Flask, render_template, request, make_response, jsonify
import tempfile
import os
import subprocess
import werkzeug
from datetime import datetime
import uuid

app = Flask(__name__)

# limit upload file size : 1MB
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
TEMP_DIR = tempfile.TemporaryDirectory()
UPLOAD_DIR = TEMP_DIR.name
print(UPLOAD_DIR)

RESOURCE_MAP = {}


@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_over_max_file_size(error):
    print("werkzeug.exceptions.RequestEntityTooLarge")
    return 'result : file size is overed.'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'upload' not in request.files:
        make_response(jsonify({'result': 'upload is required.'}))

    file = request.files['upload']
    fileName = file.filename
    if '' == fileName:
        make_response(jsonify({'result': 'filename must not empty.'}))

    saveFileName = datetime.now().strftime("%Y%m%d_%H%M%S_") \
        + werkzeug.utils.secure_filename(fileName)
    saveFilePath = os.path.join(UPLOAD_DIR, saveFileName)
    file.save(saveFilePath)

    uid = None
    while True:
        uid = str(uuid.uuid4())
        if uid not in RESOURCE_MAP:
            RESOURCE_MAP[uid] = saveFilePath
            break

    return make_response(jsonify({'result': 'upload OK', 'id': uid}))


@app.route('/approve', methods=['POST'])
def approve():
    data = request.json
    if data is None:
        return make_response(jsonify({'result': 'Content-Type must be application/json.'}))

    if data['id'] not in RESOURCE_MAP:
        return make_response(jsonify({'result': 'missing id.'}))

    if data['approve'] == 'ok':
        path = RESOURCE_MAP.pop(data['id'])
        result = str(subprocess.check_output(['md5', path]))
        os.remove(path)
        return make_response(jsonify({'result': 'approve OK', 'id': data['id'], 'md5': result}))
    else:
        path = RESOURCE_MAP.pop(data['id'])
        os.remove(path)
        return make_response(jsonify({'result': 'approve Cancel', 'id': data['id']}))


if __name__ == '__main__':
    app.run(host='localhost', port=3000, debug=True)
