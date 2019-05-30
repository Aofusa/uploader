from flask import Flask, render_template, request, make_response, jsonify
import tempfile
import os
import subprocess
import werkzeug
from datetime import datetime, timedelta
import uuid
import sched
import time
import threading

# オブジェクトとIDの対応表
RESOURCE_MAP = {}

# RESOURCE_MAP へアクセスするための スレッドロック
lock_resource_map = threading.Lock()

# 指定時間に処理を行うためのスケジューラ
scheduler = sched.scheduler(time.time, time.sleep)

app = Flask(__name__)

# limit upload file size : 1MB
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
TEMP_DIR = tempfile.TemporaryDirectory(prefix='tmp.uploader.')
UPLOAD_DIR = TEMP_DIR.name
print(UPLOAD_DIR)


@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_over_max_file_size(error):
    print("werkzeug.exceptions.RequestEntityTooLarge")
    return 'result : file size is overed.'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/resource')
def resource():
    lock_resource_map.acquire()
    result = make_response(jsonify(RESOURCE_MAP))
    lock_resource_map.release()
    return result


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

    # オブジェクトIDの割り当て
    # 重複しないものが割り当てられるまで繰り返す
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

    lock_resource_map.acquire()
    path = RESOURCE_MAP.pop(data['id'])
    lock_resource_map.release()

    if data['approve'] == 'ok':
        # 指定時間に処理したい処理内容
        def calc_hash():
            result = str(subprocess.check_output(['md5', path]))
            os.remove(path)
            print(result)

        # 別スレッドにて実行したいスケジューラ関数
        def run_schedule():
            # 現在時刻の取得
            now_time = datetime.now()
            # 現在時刻 +5秒後を実行時間にする
            scheduled_time = now_time + timedelta(seconds=5)
            # datetimeからfloatへ変換
            scheduled_time_f = float(time.mktime(scheduled_time.utctimetuple()))
            # 処理のスケジューリング
            scheduler.enterabs(scheduled_time_f, 1, calc_hash)
            scheduler.run()

        # 別スレッドの立ち上げ
        thread = threading.Thread(target=run_schedule)
        thread.start()

        return make_response(jsonify({'result': 'approve OK', 'id': data['id']}))

    else:
        os.remove(path)
        return make_response(jsonify({'result': 'approve Cancel', 'id': data['id']}))


if __name__ == '__main__':
    app.run(host='localhost', port=3000, debug=True)
