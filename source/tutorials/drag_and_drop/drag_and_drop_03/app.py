from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
  if 'file' not in request.files:
    return jsonify({'message': 'No file part'}), 400
  file = request.files['file']
  if file.filename == '':
    return jsonify({'message': 'No selected file'}), 400

  file.save(f'uploads/{file.filename}')
  return jsonify({'message': 'File uploaded successfully!'}), 200


if __name__ == '__main__':
  app.run(debug=True)
