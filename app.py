from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from forms import SourceForm
from secret import SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)

def redirect_back(default='index'):
  destination = request.args.get('next') or request.referrer or url_for(default)

  return redirect(destination)

class Source(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(512), nullable=False)
  url = db.Column(db.Unicode(512), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  def __repr__(self):
    return '<Source %r>' % self.id


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