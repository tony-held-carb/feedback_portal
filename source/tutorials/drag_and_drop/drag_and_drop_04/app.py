import os

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
  os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
  if 'file' not in request.files:
    return jsonify({'status': 'error', 'message': 'No file part'})

  file = request.files['file']
  if file.filename == '':
    return jsonify({'status': 'error', 'message': 'No selected file'})

  try:
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    return jsonify({'status': 'success', 'message': 'File uploaded successfully!'})
  except Exception as e:
    return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
  app.run(debug=True)
