import os

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
  os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
  files = request.files.getlist('file')
  file_status = []

  for file in files:
    if file:
      file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
      file.save(file_path)
      file_status.append({
        'filename': file.filename,
        'status': 'success'
      })

  return jsonify({'status': 'ok', 'files': file_status})


if __name__ == '__main__':
  app.run(debug=True)
