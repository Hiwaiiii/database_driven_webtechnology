from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    movies = db.relationship('Movie', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email=False):
        """Convert user object to dictionary for API responses"""
        data = {
            'id': self.id,
            'username': self.username,
            'movie_count': self.movies.count()
        }
        return data

    def from_dict(self, data, new_user=False):
        """Update user from dictionary data"""
        for field in ['username']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    year = db.Column(db.Integer)
    genre = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        """Convert movie object to dictionary for API responses"""
        data = {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'genre': self.genre,
            'user_id': self.user_id
        }
        return data

    def from_dict(self, data):
        """Update movie from dictionary data"""
        for field in ['title', 'year', 'genre']:
            if field in data:
                setattr(self, field, data[field])