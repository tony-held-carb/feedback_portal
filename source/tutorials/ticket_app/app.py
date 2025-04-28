import os
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)


class Ticket(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  description = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Note(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
  ticket = db.relationship('Ticket', backref=db.backref('notes', lazy=True))


class File(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  filename = db.Column(db.String(200), nullable=False)
  uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
  ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
  ticket = db.relationship('Ticket', backref=db.backref('files', lazy=True))


@app.route('/')
def index():
  tickets = Ticket.query.all()
  return render_template('index.html', tickets=tickets)


@app.route('/ticket/new', methods=['GET', 'POST'])
def new_ticket():
  if request.method == 'POST':
    title = request.form['title']
    description = request.form['description']
    ticket = Ticket(title=title, description=description)
    db.session.add(ticket)
    db.session.commit()
    flash('Ticket created successfully!', 'success')
    return redirect(url_for('index'))
  return render_template('new_ticket.html')


@app.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
def view_ticket(ticket_id):
  ticket = Ticket.query.get_or_404(ticket_id)
  if request.method == 'POST':
    if 'note' in request.form:
      content = request.form['note']
      note = Note(content=content, ticket_id=ticket.id)
      db.session.add(note)
      db.session.commit()
      flash('Note added successfully!', 'success')
    elif 'file' in request.files:
      uploaded_file = request.files['file']
      if uploaded_file.filename:
        filename = uploaded_file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(filepath)
        file_record = File(filename=filename, ticket_id=ticket.id)
        db.session.add(file_record)
        db.session.commit()
        flash('File uploaded successfully!', 'success')
    return redirect(url_for('view_ticket', ticket_id=ticket_id))
  return render_template('view_ticket.html', ticket=ticket)


@app.route('/search', methods=['GET'])
def search():
  query = request.args.get('query')
  tickets = Ticket.query.filter(Ticket.title.contains(query) | Ticket.description.contains(query)).all()
  return render_template('index.html', tickets=tickets, search=True, query=query)


if __name__ == '__main__':
  with app.app_context():
    db.create_all()
  app.run(debug=True)
