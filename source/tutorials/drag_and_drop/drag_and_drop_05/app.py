import os

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Set the folder for uploads
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
  os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
  if 'file' not in request.files:
    return jsonify({'status': 'error', 'message': 'No file part'}), 400

  file = request.files['file']

  if file.filename == '':
    return jsonify({'status': 'error', 'message': 'No selected file'}), 400

  if file:
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'status': 'success', 'message': 'File uploaded successfully!'}), 200
  else:
    return jsonify({'status': 'error', 'message': 'File upload failed'}), 500


if __name__ == '__main__':
  app.run(debug=True)
