from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, Movie

def register_routes(app):

    @app.route('/')
    @login_required
    def index():
        movies = Movie.query.filter_by(user_id=current_user.id).all()
        return render_template('index.html', movies=movies)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()

            if user is None or not user.check_password(password):
                flash('Invalid username or password')
                return redirect(url_for('login'))

            login_user(user)
            return redirect(url_for('index'))

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('register'))

            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash('Registration successful')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/add', methods=['POST'])
    @login_required
    def add_movie():
        title = request.form.get('title')
        year = request.form.get('year')

        movie = Movie(title=title, year=year, user_id=current_user.id)
        db.session.add(movie)
        db.session.commit()

        return redirect(url_for('index'))

    @app.route('/delete/<int:id>')
    @login_required
    def delete_movie(id):
        movie = Movie.query.get_or_404(id)
        if movie.user_id != current_user.id:
            flash('Unauthorized')
            return redirect(url_for('index'))

        db.session.delete(movie)
        db.session.commit()
        return redirect(url_for('index'))