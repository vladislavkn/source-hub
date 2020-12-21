from flask import Flask, render_template, send_from_directory, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Source(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(512), nullable=False)
  url = db.Column(db.Unicode(512), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  def __repr__(self):
    return '<Source %r>' % self.id


def source_form_is_invalid():
  if (not request.form['title'] or not request.form['url']):
    return True
  return False


@app.route('/', methods=['GET'])
def index():
  sources = Source.query.order_by(Source.created_at).all()
  return render_template('pages/index.html', sources=sources)


@app.route('/create', methods=['GET', 'POST'])
def create():
  if request.method == 'GET':
    return render_template('pages/create.html')

  if source_form_is_invalid():
    return render_template('pages/create.html', errors=['Fileds can not be empty'])

  try:
    title, url = request.form['title'], request.form['url']
    source = Source(title=title, url=url)
    db.session.add(source)
    db.session.commit()
  except:
    return render_template('pages/create.html', errors=['Error while saving in database. Try again later'])

  return redirect(url_for('index'))


@app.route('/source/<int:id>', methods=['GET'])
def get_source(id):
  source = Source.query.get_or_404(id)
  return render_template('pages/source.html', source=source)


@app.route('/source/<int:id>/delete', methods=['POST'])
def delete_source(id):
  source = Source.query.get_or_404(id)
  try:
    db.session.delete(source)
    db.session.commit()
  except:
    return render_template('pages/source.html', errors=['Error while deleting. Try again later'], source=source)
  return redirect(url_for('index'))


@app.route('/source/<int:id>/update', methods=['POST'])
def update_source(id):
  source = Source.query.get_or_404(id)

  if source_form_is_invalid():
    return render_template('pages/source.html', errors=['Fileds can not be empty'], source=source)

  try:
    source.title, source.url = request.form['title'], request.form['url']
    db.session.commit()
  except:
    return render_template('pages/source.html', errors=['Error while saving in database. Try again later'])

  return redirect(url_for('get_source', id=source.id))

@app.errorhandler(404)
def error_404(error):
  return render_template('pages/404.html')

if __name__ == "__main__":
  app.run(debug=True)