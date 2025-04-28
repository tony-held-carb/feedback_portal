import os

from flask import Flask, flash, redirect, render_template, request

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
  if request.method == "POST":
    if "file" not in request.files:
      flash("No file part")
      return redirect(request.url)

    file = request.files["file"]

    if file.filename == "":
      flash("No selected file")
      return redirect(request.url)

    if file:
      filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
      file.save(filepath)
      flash(f"File uploaded: {file.filename}")
      return redirect(request.url)

  return render_template("index.html")


if __name__ == "__main__":
  app.run(debug=True)
