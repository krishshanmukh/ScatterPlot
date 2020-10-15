import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename
from helper.image import findSubPlots


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
            print(file.save(os.path.join(UPLOAD_FOLDER, filename)), os.path.join(UPLOAD_FOLDER, filename))
            flash('Uploaded file')
            # return redirect(url_for('upload_file',
            #                         filename=filename))
            split_images = findSubPlots(os.path.join(app.config['UPLOAD_FOLDER'], filename), os.path.join(app.config['UPLOAD_FOLDER'], "split_" + filename))
            print(split_images)
            # return send_file(os.path.join(app.config['UPLOAD_FOLDER'], "split_" + filename), \
                # mimetype="image/png")
            return render_template("thumbnails.html", data = {'images': split_images['images'], 'main_image': split_images['main_image']})
    return render_template("upload.html")

if __name__ == '__main__':
    app.run('localhost', 5555)