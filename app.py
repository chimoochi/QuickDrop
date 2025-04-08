from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import socket
import threading
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        wrapped_file = ProgressFileWrapper(file, file_size)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


local_ip = socket.gethostbyname(socket.gethostname())
port = 5000
def print_server_info():
    time.sleep(2) 
    for i in range(5):
        print("\n")
    print(f"\nLink to share:")
    print(f"http://{local_ip}:{port}")
threading.Thread(target=print_server_info).start()

app.run(host="0.0.0.0", port=port, debug=False)
