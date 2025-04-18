from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import socket
import threading
import time
import re
import qrcode
import math
import subprocess
import sys
import random
import string


port = 5012

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

temppassword = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    password = request.args.get('password', '')
    if password != temppassword:
        return "Invalid password", 403
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f != '.DS_Store']
    return render_template('index.html', files=files)


@app.route('/upload', methods=['POST'])
def upload_file():
    password = request.args.get('password', '')
    if password!= temppassword:
        return "Invalid password", 403
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file.seek(0, os.SEEK_END)
        file.seek(0)
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return redirect(f"/?password={temppassword}")

@app.route('/download/<filename>')
def download_file(filename):
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    return "File not found", 404

@app.route('/preview/<filename>')
def preview_file(filename):
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return "File not found", 404

def show_image(image_path):
    # Create a separate process for the Tkinter window
    # This ensures it runs on its own main thread but its dumb
    # Create a small Python script to display the QR code
    script = f"""
import tkinter as tk
from PIL import Image, ImageTk
import time
import os
def show():
    root = tk.Tk()
    root.title("file sharing over LAN")
    
    # Create a frame for the content
    content_frame = tk.Frame(root)
    content_frame.pack(padx=10, pady=10)
    
    # Add instructions text
    instructions = tk.Label(content_frame, 
                           text="Scan QR code to link to website.\\nMake sure devices are on the same WiFi network.",
                           font=("Arial", 12), justify=tk.CENTER)
    instructions.pack(pady=(0, 10))
    
    # Display QR code
    img = Image.open(r"{image_path}")
    tk_img = ImageTk.PhotoImage(img)
    label = tk.Label(content_frame, image=tk_img)
    label.pack()
    label.image = tk_img
    
    # Bring window to front
    root.lift()
    root.attributes('-topmost', True)
    for i in range(5):
        root.lift()
        root.after_idle(root.attributes, '-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
    if os.path.exists(r"{image_path}"):
        os.remove(r"{image_path}")
    root.after_idle(root.attributes, '-topmost', False)
    
    root.mainloop()
    

show()
"""
    
    # Run the script in a separate process because for some reason, tkinter is like that. wierdo 🤬
    subprocess.Popen([sys.executable, '-c', script])

def get_local_ip():
    try:
        # Create a socket that doesn't actually connect
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # This triggers the OS to figure out which interface would be used
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fallback to the original method
        return socket.gethostbyname(socket.gethostname())

local_ip = get_local_ip() #socket.gethostbyname(socket.gethostname()) 


def print_server_info():
    print(f"\nLink to share:")
    print(f"http://{local_ip}:{port}?password={temppassword}")
    img = qrcode.make(f"http://{local_ip}:{port}?password={temppassword}")
    img.save("qrcode.png")
    show_image(os.path.join(os.path.dirname(os.path.abspath(__file__)), "qrcode.png"))

threading.Thread(target=print_server_info).start()


app.run(host="0.0.0.0", port=port, debug=False)
