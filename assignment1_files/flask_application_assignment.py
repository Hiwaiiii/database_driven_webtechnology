from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'movies.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Movie model representing the movies table
class Movie(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    number_of_oscars = db.Column(db.Integer, nullable=False)

# Create the database and the tables for the model
with app.app_context():
    db.create_all()

    if Movie.query.count() == 0:
        movies = [
            Movie(title="Inception", year=2010, number_of_oscars=4),
            Movie(title="The Dark Knight", year=2008, number_of_oscars=2),
            Movie(title="The Godfather", year=1972, number_of_oscars=3),
            Movie(title="Shawshank Redemption", year=1994, number_of_oscars=5)
        ]
        db.session.add_all(movies)
        db.session.commit()

@app.route('/', methods=['GET'])
def index():
    movies = Movie.query.all()
    return render_template('index_incomplete.html', movies=movies)

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        number_of_oscars = request.form['number_of_oscars']
        new_movie = Movie(title=title, year=year, number_of_oscars=number_of_oscars)
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_movie_incomplete.html')

@app.route('/edit_movie/<int:id>', methods=['GET', 'POST'])
def edit_movie(id):
    movie = Movie.query.get_or_404(id)

    if request.method == 'POST':
        movie.title = request.form['title']
        movie.year = request.form['year']
        movie.number_of_oscars = request.form['number_of_oscars']

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_movie.html', movie=movie)

@app.route('/delete_movie/<int:id>')
def delete_movie(id):
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
