import os
import sys
import shutil
sys.path.append(os.path.join(sys.path[0],'trainedmodel'))
from flask import Flask, flash, request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename
from helper.image import findSubPlots
from trainedmodel import detect

# Create two constant. They direct to the app root folder and logo upload folder
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getFileNameWithoutExtension(file):
    file_name = os.path.basename(file)
    index_of_dot = file_name.index('.')
    file_name_without_extension = file_name[:index_of_dot]
    return file_name_without_extension

@app.route('/', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        print(request.files)
        if 'imageInput' not in request.files:
            flash('No file part')
            return redirect(url_for('upload_file'))
        file = request.files['imageInput']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filenameWithoutExtension = getFileNameWithoutExtension(filename)
            print(filenameWithoutExtension)
            print(os.path.join(app.config['UPLOAD_FOLDER'], filenameWithoutExtension))
            fileDirectory = os.path.join(app.config['UPLOAD_FOLDER'], filenameWithoutExtension)
            if os.path.exists(fileDirectory):
                shutil.rmtree(fileDirectory)
            os.mkdir(fileDirectory)
            os.mkdir(os.path.join(fileDirectory, 'test')) 
            file.save(os.path.join(fileDirectory, filename))
            print(os.path.join(UPLOAD_FOLDER, filename))
            flash('Uploaded file')
            # return redirect(url_for('upload_file',
            #                         filename=filename))

            split_images = findSubPlots(os.path.join(fileDirectory, filename), os.path.join(fileDirectory, "split_" + filename))
            print(split_images)
            # return send_file(os.path.join(app.config['UPLOAD_FOLDER'], "split_" + filename), \
                # mimetype="image/png")
            return render_template("thumbnails.html", data = {'images': split_images['images'], 'main_image': split_images['main_image']
            ,'folderName': filenameWithoutExtension})
    return render_template("upload.html")

@app.route('/runDetections', methods=['GET', 'POST'])
def runDetection():
    print("inside runDetection")
    if request.method == 'POST':
        print(request.form.keys)
        folderName = request.form['folderName']
        imgPointsDict = detect.detectPoints(folderName)


    return redirect('/')

if __name__ == '__main__':
    app.run('localhost', 5555)