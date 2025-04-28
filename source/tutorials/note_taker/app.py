from datetime import datetime

from flask import Flask, flash, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

from forms import NoteForm

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)

# from models import Note

# class Note(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   title = db.Column(db.String(100), nullable=False)
#   content = db.Column(db.Text, nullable=False)
#   username = db.Column(db.String(50), nullable=False)
#   created_at = db.Column(db.DateTime, nullable=False)
#   updated_at = db.Column(db.DateTime, nullable=False)

with app.app_context():
  db.create_all()


@app.route('/')
def home():
  notes = Note.query.all()
  return render_template('home.html', notes=notes)


@app.route('/note/new', methods=['GET', 'POST'])
def new_note():
  form = NoteForm()
  if form.validate_on_submit():
    new_note = Note(
      title=form.title.data,
      content=form.content.data,
      username=form.username.data,
      created_at=datetime.utcnow(),
      updated_at=datetime.utcnow()
    )
    db.session.add(new_note)
    db.session.commit()
    flash('Note created successfully!', 'success')
    return redirect(url_for('home'))
  return render_template('note_form.html', form=form)


@app.route('/note/<int:note_id>')
def note_detail(note_id):
  note = Note.query.get_or_404(note_id)
  return render_template('note.html', note=note)


@app.route('/note/<int:note_id>/edit', methods=['GET', 'POST'])
def edit_note(note_id):
  note = Note.query.get_or_404(note_id)
  form = NoteForm(obj=note)
  if form.validate_on_submit():
    note.title = form.title.data
    note.content = form.content.data
    note.username = form.username.data
    note.updated_at = datetime.utcnow()
    db.session.commit()
    flash('Note updated successfully!', 'success')
    return redirect(url_for('note_detail', note_id=note.id))
  return render_template('note_form.html', form=form, note=note)


@app.route('/note/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
  note = Note.query.get_or_404(note_id)
  db.session.delete(note)
  db.session.commit()
  flash('Note deleted successfully!', 'success')
  return redirect(url_for('home'))


if __name__ == '__main__':
  app.run(debug=True)
