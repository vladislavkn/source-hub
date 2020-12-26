from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from forms import SourceForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret_key_for_development_mode')
db = SQLAlchemy(app)
login_manager = LoginManager(app)

def redirect_back(default='index'):
  destination = request.args.get('next') or request.referrer or url_for(default)

  return redirect(destination)

@login_manager.user_loader
def load_user(user_id):
  return db.session.query(User).get(user_id)

class User(db.Model, UserMixin):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(512), nullable=False, unique=True)
  password_hash = db.Column(db.String(512), nullable=False)
  sources = db.relationship('Source', backref='author')
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  def set_password(self, password):
	  self.password_hash = generate_password_hash(password)

  def check_password(self,  password):
	  return check_password_hash(self.password_hash, password)

  def __repr__(self):
    return f'<User {self.id}:{self.name}>'

class Source(db.Model):
  __tablename__ = 'sources'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(512), nullable=False)
  url = db.Column(db.Unicode(512), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  author_id = db.Column(db.Integer(), db.ForeignKey('users.id'))

  def __repr__(self):
    return f'<Source {self.id}>'


@app.route('/', methods=['GET'])
def index():
  sources = Source.query.order_by(Source.created_at).all()
  return render_template('pages/index.html', sources=sources)


@app.route('/create', methods=['GET', 'POST'])
def create():
  form = SourceForm()
  if form.validate_on_submit():
    try:
      title, url = form.title.data, form.url.data
      source = Source(title=title, url=url)
      db.session.add(source)
      db.session.commit()
    except:
      flash('Error while saving in database. Try again later', 'error')
    else:
      flash("Source created", "success")
      return redirect(url_for('index'))

  return render_template('pages/create.html', form=form)

@app.route('/source/<int:id>', methods=['GET', 'POST'])
def source_edit(id):
  source = Source.query.get_or_404(id)
  form = SourceForm(obj=source)

  if form.validate_on_submit():
    try:
      source.title, source.url = form.title.data, form.url.data
      db.session.commit()
    except:
      flash('Error while saving in database. Try again later', 'error')
    else:
      flash("Source saved", "success")

  return render_template('pages/source-edit.html', source=source, form=form)


@app.route('/source/<int:id>/delete', methods=['POST'])
def delete_source(id):
  source = Source.query.get_or_404(id)
  try:
    db.session.delete(source)
    db.session.commit()
  except:
    flash('Error while deleting. Try again later', 'error')
    return redirect_back()

  flash("Source deleted", "success")
  return redirect(url_for('index'))


@app.errorhandler(404)
def error_404(error):
  return render_template('pages/404.html')

if __name__ == "__main__":
  app.run(debug=True)