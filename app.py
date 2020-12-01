import os
import sys
import shutil
sys.path.append(os.path.join(sys.path[0],'trainedmodel'))
from flask import Flask, flash, request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename
from helper.image import findSubPlots
from trainedmodel import detect
from distances import findClosestPoints

# Create two constant. They direct to the app root folder and logo upload folder
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join('static', 'uploads')
PREDICTED_FOLDER = os.path.join('static', 'predicted')
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
            os.makedirs(fileDirectory, exist_ok=True)
            os.mkdir(os.path.join(fileDirectory, 'test')) 
            file_path = os.path.join(fileDirectory, 'source'+filename[filename.rfind("."):])
            file.save(file_path)
            print(file_path)
            flash('Uploaded file')
            # return redirect(url_for('upload_file',
            #                         filename=filename))

            split_images = findSubPlots(file_path, os.path.join(fileDirectory, "split_" + filename))
            print("split", split_images)
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
        column_values = []
        for i in range(100):
            if "ColumnLowerBound" + str(i) in request.form.keys():
                lower = int(request.form["ColumnLowerBound" + str(i)])
                upper = int(request.form["ColumnUpperBound" + str(i)])
                column_values.append((lower, upper))
        imgPointsDict, img_shape = detect.detectPoints(folderName, column_values)
        # print(imgPointsDict)
        PLTS_PTS = []
        DATA = []
        for val in imgPointsDict.values():
            x, y = [], []
            PTS = []
            for v in val:
                x.append(v[0])
                y.append(v[1])
                PTS.append((v[0], v[1]))
            import matplotlib.pyplot as plt
            PLTS_PTS.append(PTS)

        for pt1 in PLTS_PTS[-1]:
            # overall point
            pt = [pt1[0], pt1[1]]
            flag = True
            # print(len(PLTS_PTS[1::-1]), len(PLTS_PTS))
            for pt2 in PLTS_PTS[::-1][1:]:
                y = findClosestPoints(pt1, pt2)
                if y != -1:
                    pt.append(y)
                else:
                    flag = False
            if flag:
                DATA.append(pt)
                # print(pt)
        # DATA.append([0 for _ in range(len(DATA[0]))])
        # DATA.append([img_shape[1] for _ in range(len(DATA[0]))])
        import seaborn as sns
        import pandas as pd
        sns.set_theme(style="ticks")
        df = pd.DataFrame(DATA, columns = [str(i) for i in range(len(DATA[0]))])
        sns.pairplot(df)
        import  csv

        fileDirectory = os.path.join(PREDICTED_FOLDER, folderName, 'data')
        os.makedirs(fileDirectory, exist_ok=True)

        with open(os.path.join(fileDirectory, "data.csv"),"w") as f:
            wr = csv.writer(f)
            wr.writerows(DATA)
        plt.savefig(os.path.join(PREDICTED_FOLDER, folderName, 'source.png'))

        images, main_image = [], [""]*2
        for files in os.listdir(os.path.join(PREDICTED_FOLDER, folderName)):
            if os.path.isfile(os.path.join(PREDICTED_FOLDER, folderName, files)):
                if files.find("source") != -1:
                    main_image[1] = os.path.join(PREDICTED_FOLDER, folderName, files)
                    break
        for files in os.listdir(os.path.join(UPLOAD_FOLDER, folderName)):
            if os.path.isfile(os.path.join(UPLOAD_FOLDER, folderName, files)):
                if files.find("source") != -1:
                    main_image[0] = os.path.join(UPLOAD_FOLDER, folderName, files)
                    break
        for files in os.listdir(os.path.join(UPLOAD_FOLDER, folderName, "test")):
            if os.path.isfile(os.path.join(UPLOAD_FOLDER, folderName, "test", files)):
                images.append((os.path.join(UPLOAD_FOLDER, folderName, 'test', files), 
                os.path.join(PREDICTED_FOLDER, folderName, 'test', files)))
                print("FIle inn 131", files)
        print(main_image, images)
        return render_template("output.html", data = {'main_image':main_image, 'images': images })
    return render_template("upload.html")

if __name__ == '__main__':
    app.run('localhost', 5555)