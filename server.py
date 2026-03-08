#!/usr/bin/env python3
"""
听写小助手 - 后端服务（Web Station WSGI 模式）
Callable: app
数据存储在脚本同目录下的 data/dictation_data.json
"""
from flask import Flask, request, jsonify, send_from_directory, Response
import json, os, threading
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATA_FILE = os.path.join(DATA_DIR, 'dictation_data.json')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, static_folder=STATIC_DIR)
_lock = threading.Lock()

DEFAULT_DATA = {
    "wordLists": [],
    "mistakes": {},
    "history": [],
    "settings": {"rate": 0.8, "repeat": 2}
}

os.makedirs(DATA_DIR, exist_ok=True)

def read_data():
    with _lock:
        if not os.path.exists(DATA_FILE):
            return dict(DEFAULT_DATA)
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return dict(DEFAULT_DATA)

def write_data(data):
    with _lock:
        tmp = DATA_FILE + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, DATA_FILE)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(read_data())

@app.route('/api/data', methods=['POST'])
def save_data():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'no data'}), 400
    write_data(data)
    return jsonify({'ok': True})

@app.route('/api/backup', methods=['GET'])
def backup():
    data = read_data()
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename=dictation_backup_{ts}.json'}
    )

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)

# WSGI 入口 — Web Station 的 Callable 填 app
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"启动中，端口 {port}，数据目录 {DATA_DIR}")
    app.run(host='0.0.0.0', port=port, debug=False)
