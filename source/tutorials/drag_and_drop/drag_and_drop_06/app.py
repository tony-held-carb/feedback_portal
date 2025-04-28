import os

from flask import Flask, jsonify, render_template, request, url_for

app = Flask(__name__)

# Configure the upload folder
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
  os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
  if 'file' not in request.files:
    return jsonify({'error': 'No file part'}), 400

  file = request.files['file']
  if file.filename == '':
    return jsonify({'error': 'No selected file'}), 400

  # Save the file
  file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
  file.save(file_path)

  return jsonify({'success': True, 'redirect_url': url_for('index')})


if __name__ == "__main__":
  app.run(debug=True)
