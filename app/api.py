from flask import Blueprint, jsonify, request, g
from werkzeug.http import HTTP_STATUS_CODES
from functools import wraps
from app import db
from app.models import User, Movie

api = Blueprint('api', __name__)

def success_response(data, status_code=200):
    """Return successful JSON response"""
    response = jsonify(data)
    response.status_code = status_code
    return response

def error_response(status_code, message=None):
    """Return error JSON response"""
    payload = {
        'error': HTTP_STATUS_CODES.get(status_code, 'Unknown Error')
    }
    if message:
        payload['details'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response

def authenticate_request(f):
    """Verify token and load user for protected endpoints"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        if not auth_header:
            return error_response(401, 'Missing authentication token')

        token = auth_header.replace('Bearer ', '').strip()

        if not token:
            return error_response(401, 'Invalid token format')

        user = User.verify_auth_token(token)

        if not user:
            return error_response(401, 'Token is invalid or has expired')

        g.authenticated_user = user

        return f(*args, **kwargs)

    return wrapper

@api.route('/token', methods=['POST'])
def authenticate():
    """Issue authentication token for valid credentials"""
    request_data = request.get_json()

    if not request_data:
        return error_response(400, 'Request body must be JSON')

    username = request_data.get('username')
    password = request_data.get('password')

    if not username or not password:
        return error_response(400, 'Both username and password are required')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return error_response(401, 'Invalid username or password')

    token = user.generate_auth_token()
    db.session.commit()

    return success_response({
        'token': token,
        'user_id': user.id,
        'username': user.username,
        'expires_in': 3600
    })

@api.route('/movies', methods=['GET'])
@authenticate_request
def list_movies():
    """Retrieve all movies owned by authenticated user"""
    user_movies = Movie.query.filter_by(user_id=g.authenticated_user.id).all()

    return success_response({
        'movies': [m.to_dict() for m in user_movies],
        'count': len(user_movies)
    })

@api.route('/movies/<int:movie_id>', methods=['GET'])
@authenticate_request
def retrieve_movie(movie_id):
    """Get details of a specific movie"""
    movie = Movie.query.get_or_404(movie_id)

    if movie.user_id != g.authenticated_user.id:
        return error_response(403, 'You do not have access to this movie')

    return success_response(movie.to_dict())

@api.route('/movies', methods=['POST'])
@authenticate_request
def add_movie():
    """Create a new movie entry"""
    request_data = request.get_json()

    if not request_data:
        return error_response(400, 'Request body must be JSON')

    title = request_data.get('title')
    if not title:
        return error_response(400, 'Movie title is required')

    new_movie = Movie(
        title=title,
        year=request_data.get('year'),
        user_id=g.authenticated_user.id
    )

    db.session.add(new_movie)
    db.session.commit()

    response = success_response(new_movie.to_dict(), 201)
    response.headers['Location'] = f'/api/movies/{new_movie.id}'
    return response

@api.route('/movies/<int:movie_id>', methods=['PUT'])
@authenticate_request
def modify_movie(movie_id):
    """Update an existing movie"""
    movie = Movie.query.get_or_404(movie_id)

    if movie.user_id != g.authenticated_user.id:
        return error_response(403, 'You do not have access to this movie')

    request_data = request.get_json()

    if not request_data:
        return error_response(400, 'Request body must be JSON')

    movie.from_dict(request_data)
    db.session.commit()

    return success_response(movie.to_dict())

@api.route('/movies/<int:movie_id>', methods=['DELETE'])
@authenticate_request
def remove_movie(movie_id):
    """Delete a movie"""
    movie = Movie.query.get_or_404(movie_id)

    if movie.user_id != g.authenticated_user.id:
        return error_response(403, 'You do not have access to this movie')

    db.session.delete(movie)
    db.session.commit()

    return '', 204

@api.route('/users', methods=['POST'])
def register_user():
    """Create a new user account"""
    request_data = request.get_json()

    if not request_data:
        return error_response(400, 'Request body must be JSON')

    username = request_data.get('username')
    password = request_data.get('password')

    if not username or not password:
        return error_response(400, 'Both username and password are required')

    if User.query.filter_by(username=username).first():
        return error_response(400, 'Username already taken')

    # Create new user
    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    response = success_response(new_user.to_dict(), 201)
    response.headers['Location'] = f'/api/users/{new_user.id}'
    return response

@api.route('/users/<int:user_id>', methods=['GET'])
@authenticate_request
def get_user_profile(user_id):
    """Retrieve user profile information"""
    if user_id != g.authenticated_user.id:
        return error_response(403, 'You can only access your own profile')

    user = User.query.get_or_404(user_id)
    return success_response(user.to_dict())