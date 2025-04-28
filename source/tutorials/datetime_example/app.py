from datetime import datetime

from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'


# Define the form
class DateForm(FlaskForm):
  datetime_field = DateTimeLocalField('Pick a Date and Time', format='%Y-%m-%dT%H:%M')


@app.route('/', methods=['GET'])
def index():
  form = DateForm()

  # Set the DateTimeLocalField to a specific datetime
  form.datetime_field.data = datetime(2023, 11, 14, 15, 30)  # Example datetime

  return render_template('index.html', form=form)


if __name__ == '__main__':
  app.run(debug=True)
