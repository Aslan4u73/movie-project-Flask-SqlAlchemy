from models import db, User, Movie


class DataManager:
    """Manages all database operations for users and movies."""

    def __init__(self, app):
        """Initialize with Flask app for database context."""
        self.app = app

    def get_all_users(self):
        """Return a list of all users."""
        return User.query.all()

    def get_user(self, user_id):
        """Return a single user by ID or None."""
        return User.query.get(user_id)

    def add_user(self, name):
        """Add a new user to the database."""
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_user_movies(self, user_id):
        """Return all movies for a specific user."""
        user = User.query.get(user_id)
        if user:
            return user.movies
        return []

    def add_movie(self, user_id, name, director, year, rating, poster_url=''):
        """Add a new movie to a user s favorite list."""
        new_movie = Movie(
            name=name,
            director=director,
            year=year,
            rating=rating,
            poster_url=poster_url,
            user_id=user_id
        )
        db.session.add(new_movie)
        db.session.commit()
        return new_movie

    def get_movie(self, movie_id):
        """Return a single movie by ID."""
        return Movie.query.get(movie_id)

    def update_movie(self, movie_id, name, director, year, rating):
        """Update movie details."""
        movie = Movie.query.get(movie_id)
        if movie:
            movie.name = name
            movie.director = director
            movie.year = year
            movie.rating = rating
            db.session.commit()
        return movie

    def delete_movie(self, movie_id):
        """Delete a movie from the database."""
        movie = Movie.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return True
        return False
