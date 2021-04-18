
from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
import os
import threading
from .functions import *
from .sql import *


app = Flask(__name__)

app.config["IMAGE_UPLOADS"] = './libs'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["txt"]



@app.route('/', methods=['POST', 'GET'])
def index():

    machines = Machines.get()

    return render_template('index.html', machines=machines)

@app.route('/decrypt', methods=['POST', 'GET'])
def decrypt():
    files = []
    for filename in os.listdir("./libs"):
        if filename.endswith(".txt"):
            files.append({'name':filename[:-4]})

    mode = Hashes.hashes_get()
    if request.method == 'POST':
        print(request.form)
        decrypt_work_queue(request.form)

    return render_template('decrypt.html', mode=mode, files=files) 
    

@app.route('/decrypted', methods=['GET'])
def decrypted():

    decryptions = Decrypted.everything()
    algos = Hashes.hashes_get()

    return render_template('decrypted.html', decryptions=decryptions, algos=algos)

@app.route('/overview', methods=['POST', 'GET'])
def overview():
    ongoing_queue = Ongoing_job.full_queue()
    task_queue = Decrypt_queue.full_queue()
    algos = Hashes.hashes_get()
    
    return render_template('overview.html', ongoing_queue = ongoing_queue,
    task_queue = task_queue, algos = algos)



	
@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']

        if f.filename == "":
            print("No filename")
            return redirect(request.url)

        f.save(os.path.join(app.config["IMAGE_UPLOADS"], f.filename))
        return render_template('upload.html')
    
    return render_template('upload.html')
