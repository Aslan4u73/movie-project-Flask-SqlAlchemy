import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db
from data_manager import DataManager

# OMDb API configuration
API_KEY = "61bf20b9"
API_URL = "http://www.omdbapi.com/"

# Create Flask app
app = Flask(__name__)
app.secret_key = "moviweb-secret-key-2024"

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'instance', 'movies.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database with app
db.init_app(app)

# Create tables if they dont exist
with app.app_context():
    db.create_all()

# Initialize DataManager
data_manager = DataManager(app)


def fetch_movie_data(title):
    """Fetch movie data from OMDb API by title."""
    try:
        response = requests.get(
            API_URL, params={"apikey": API_KEY, "t": title}
        )
        data = response.json()
        if data.get("Response") == "True":
            year_str = data.get("Year", "0")[:4]
            rating_str = data.get("imdbRating", "0")
            return {
                "name": data.get("Title", title),
                "director": data.get("Director", "Unknown"),
                "year": int(year_str) if year_str.isdigit() else 0,
                "rating": float(rating_str) if rating_str != "N/A" else 0.0,
                "poster_url": data.get("Poster", ""),
            }
        return None
    except Exception:
        return None


@app.route("/")
def home():
    """Home page - show all users and add user form."""
    users = data_manager.get_all_users()
    return render_template("index.html", users=users)


@app.route("/users", methods=["POST"])
def add_user():
    """Add a new user."""
    name = request.form.get("name", "").strip()
    if not name:
        flash("Name cannot be empty.", "danger")
        return redirect(url_for("home"))
    data_manager.add_user(name)
    flash(f"User '{name}' added successfully!", "success")
    return redirect(url_for("home"))


@app.route("/users/<int:user_id>/movies")
def user_movies(user_id):
    """Show all movies for a specific user."""
    user = data_manager.get_user(user_id)
    if not user:
        return render_template("404.html", message="User not found"), 404
    movies = data_manager.get_user_movies(user_id)
    return render_template("movies.html", user=user, movies=movies)


@app.route("/users/<int:user_id>/add_movie", methods=["GET", "POST"])
def add_movie(user_id):
    """Add a movie to a users list."""
    user = data_manager.get_user(user_id)
    if not user:
        return render_template("404.html", message="User not found"), 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Movie title cannot be empty.", "danger")
            return redirect(url_for("add_movie", user_id=user_id))

        # Try to fetch from OMDb API
        movie_data = fetch_movie_data(title)
        if movie_data:
            data_manager.add_movie(
                user_id=user_id,
                name=movie_data["name"],
                director=movie_data["director"],
                year=movie_data["year"],
                rating=movie_data["rating"],
                poster_url=movie_data.get("poster_url", ""),
            )
            flash(f"Movie '{movie_data['name']}' added!", "success")
        else:
            # Manual fallback
            name = request.form.get("title", title)
            director = request.form.get("director", "Unknown")
            year = request.form.get("year", 0)
            rating = request.form.get("rating", 0)
            try:
                year = int(year) if year else 0
                rating = float(rating) if rating else 0.0
            except ValueError:
                year, rating = 0, 0.0
            data_manager.add_movie(user_id, name, director, year, rating)
            flash(f"Movie '{name}' added manually.", "success")

        return redirect(url_for("user_movies", user_id=user_id))

    return render_template("add_movie.html", user=user)


@app.route(
    "/users/<int:user_id>/movies/<int:movie_id>/update",
    methods=["GET", "POST"],
)
def update_movie(user_id, movie_id):
    """Update a movie in a users list."""
    user = data_manager.get_user(user_id)
    movie = data_manager.get_movie(movie_id)
    if not user or not movie:
        return render_template("404.html", message="Not found"), 404

    if request.method == "POST":
        name = request.form.get("name", movie.name)
        director = request.form.get("director", movie.director)
        year = request.form.get("year", movie.year)
        rating = request.form.get("rating", movie.rating)
        try:
            year = int(year) if year else movie.year
            rating = float(rating) if rating else movie.rating
        except ValueError:
            year, rating = movie.year, movie.rating
        data_manager.update_movie(movie_id, name, director, year, rating)
        flash(f"Movie '{name}' updated!", "success")
        return redirect(url_for("user_movies", user_id=user_id))

    return render_template("update_movie.html", user=user, movie=movie)


@app.route(
    "/users/<int:user_id>/movies/<int:movie_id>/delete",
    methods=["POST"],
)
def delete_movie(user_id, movie_id):
    """Delete a movie from a users list."""
    movie = data_manager.get_movie(movie_id)
    if movie:
        data_manager.delete_movie(movie_id)
        flash(f"Movie '{movie.name}' deleted.", "success")
    else:
        flash("Movie not found.", "danger")
    return redirect(url_for("user_movies", user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error page."""
    return render_template("404.html", message="Page not found"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
