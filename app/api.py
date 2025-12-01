from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Movie, User
from werkzeug.http import HTTP_STATUS_CODES

api = Blueprint('api', __name__)

def error_response(status_code, message=None):
    """Generate error response in JSON format"""
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response

def bad_request(message):
    """Return a 400 bad request error"""
    return error_response(400, message)

@api.route('/movies', methods=['GET'])
@login_required
def get_movies():
    """Get all movies for the current user"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    movies = Movie.query.filter_by(user_id=current_user.id).paginate(
        page=page, per_page=per_page, error_out=False
    )

    data = {
        'items': [movie.to_dict() for movie in movies.items],
        'meta': {
            'page': page,
            'per_page': per_page,
            'total_pages': movies.pages,
            'total_items': movies.total
        }
    }
    return jsonify(data)

@api.route('/movies/<int:id>', methods=['GET'])
@login_required
def get_movie(id):
    """Get a specific movie by ID"""
    movie = Movie.query.get_or_404(id)

    if movie.user_id != current_user.id:
        return error_response(403, 'Access denied')

    return jsonify(movie.to_dict())

@api.route('/movies', methods=['POST'])
@login_required
def create_movie():
    """Create a new movie"""
    data = request.get_json() or {}

    if 'title' not in data:
        return bad_request('Must include title field')

    movie = Movie(user_id=current_user.id)
    movie.from_dict(data)
    db.session.add(movie)
    db.session.commit()

    response = jsonify(movie.to_dict())
    response.status_code = 201
    response.headers['Location'] = f'/api/movies/{movie.id}'
    return response

@api.route('/movies/<int:id>', methods=['PUT'])
@login_required
def update_movie(id):
    """Update an existing movie"""
    movie = Movie.query.get_or_404(id)

    if movie.user_id != current_user.id:
        return error_response(403, 'Access denied')

    data = request.get_json() or {}
    movie.from_dict(data)
    db.session.commit()

    return jsonify(movie.to_dict())

@api.route('/movies/<int:id>', methods=['DELETE'])
@login_required
def delete_movie(id):
    """Delete a movie"""
    movie = Movie.query.get_or_404(id)

    if movie.user_id != current_user.id:
        return error_response(403, 'Access denied')

    db.session.delete(movie)
    db.session.commit()

    return '', 204


@api.route('/users/<int:id>', methods=['GET'])
@login_required
def get_user(id):
    """Get user information"""
    if id != current_user.id:
        return error_response(403, 'Access denied')

    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())

@api.route('/users', methods=['POST'])
def create_user():
    """Register a new user"""
    data = request.get_json() or {}

    if 'username' not in data or 'password' not in data:
        return bad_request('Must include username and password fields')

    if User.query.filter_by(username=data['username']).first():
        return bad_request('Username already exists')

    user = User(username=data['username'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = f'/api/users/{user.id}'
    return response