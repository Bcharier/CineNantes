from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TheaterModel(db.Model):
    __tablename__ = "theaters"
    id = db.Column(db.Integer, primary_key=True)
    internal_id = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    url = db.Column(db.String)

    showtimes = db.relationship("ShowtimeModel", back_populates="theater", cascade="all, delete-orphan")

class MovieModel(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    allocine_id = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    runtime = db.Column(db.String)
    synopsis = db.Column(db.Text)
    genres = db.Column(db.String)
    actors = db.Column(db.String)
    director = db.Column(db.String)
    affiche = db.Column(db.String)
    url = db.Column(db.String)

    showtimes = db.relationship("ShowtimeModel", back_populates="movie", cascade="all, delete-orphan")

class ShowtimeModel(db.Model):
    __tablename__ = "showtimes"
    id = db.Column(db.Integer, primary_key=True)
    starts_at = db.Column(db.DateTime, nullable=False, index=True)
    diffusion_version = db.Column(db.String)
    services = db.Column(db.String)

    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False)
    theater_id = db.Column(db.Integer, db.ForeignKey("theaters.id"), nullable=False)

    movie = db.relationship("MovieModel", back_populates="showtimes")
    theater = db.relationship("TheaterModel", back_populates="showtimes")