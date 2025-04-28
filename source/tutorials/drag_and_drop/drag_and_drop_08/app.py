import os

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
print(f"In app.py drag and drop 08")

# Set upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
  os.makedirs(UPLOAD_FOLDER)


# Index route: list files in the uploads folder
@app.route('/')
def index():
  print(f"in index app 8")
  files = os.listdir(app.config['UPLOAD_FOLDER'])
  return render_template('index_01.html', files=files)


# Upload route: drag and drop upload functionality
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
  print(f"{request.files=}")
  if request.method == 'POST':
    if 'file' not in request.files:
      return redirect(request.url)
    print(f"{request.files['file']=}")
    file = request.files['file']
    if file.filename == '':
      return redirect(request.url)
    if file:
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      return redirect(url_for('index'))
  return render_template('upload.html')


if __name__ == '__main__':
  app.run(debug=True)
