import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Uploaded file')
            return redirect(url_for('upload_file',
                                    filename=filename))
    return render_template("upload.html")

if __name__ == '__main__':
    app.run('localhost', 5555)