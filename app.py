# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)

movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


directors_schema = DirectorSchema(many=True)
director_schema = DirectorSchema()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


genres_schema = GenreSchema(many=True)
genre_schema = GenreSchema()


@movie_ns.route('/')
class MoviesView(Resource):

    def get(self):
        query_on_dir = request.args.get('director_id')
        query_on_genre = request.args.get('genre_id')
        if query_on_dir and query_on_genre and query_on_dir != '' and query_on_genre != '':
            movies_list = db.session.query(Movie).filter(Movie.director_id == query_on_dir,
                                                         Movie.genre_id == query_on_genre)
        elif query_on_dir and query_on_dir != '':
            movies_list = db.session.query(Movie).filter(Movie.director_id == query_on_dir)
        elif query_on_genre and query_on_genre != '':
            movies_list = db.session.query(Movie).filter(Movie.genre_id == query_on_genre)
        else:
            movies_list = Movie.query.all()
        return movies_schema.dump(movies_list), 200

    def post(self):
        movie_data = movie_schema.loads(request.data)
        db.session.add(Movie(**movie_data))
        db.session.commit()
        return '', 201




@movie_ns.route('/<int:mid>')
class MovieView(Resource):



    def get(self, mid):
        try:
            get_movie = db.session.query(Movie).filter(Movie.id == mid).one()
            return movie_schema.dump(get_movie), 200
        except Exception as e:
            return str(e), 404

    def put(self, mid):
        movie = Movie.query.get(mid)
        movie_data = movie_schema.loads(request.data)
        movie.title = movie_data['title']
        movie.description = movie_data['description']
        movie.trailer = movie_data['trailer']
        movie.year = movie_data['year']
        movie.rating = movie_data['rating']
        movie.genre_id = movie_data['genre_id']
        movie.director_id = movie_data['director_id']
        db.session.commit()
        return '', 204

    def delete(self,mid):
        movie = Movie.query.get(mid)
        db.session.delete(movie)
        db.session.commit()
        return '', 204


@director_ns.route('/')
class DirectorsView(Resource):

    def get(self):
        directors = Director.query.all()
        return directors_schema.dump(directors), 200

    def post(self):
        director_data = director_schema.loads(request.data)
        db.session.add(Director(**director_data))
        db.session.commit()
        return '', 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):

    def get(self, did):
        try:
            director = db.session.query(Director).filter(Director.id == did).one()
            return director_schema.dump(director), 200
        except Exception as e:
            return str(e), 404

    def put(self, did):
        director = Director.query.get(did)
        director_data = director_schema.loads(request.data)
        director.name = director_data['name']
        db.session.commit()
        return '', 204

    def delete(self, did):
        director = Director.query.get(did)
        db.session.delete(director)
        db.session.commit()
        return '', 204


@genre_ns.route('/')
class GenresView(Resource):

    def get(self):
        genres = Genre.query.all()
        return genres_schema.dump(genres), 200

    def post(self):
        genre_data = genre_schema.loads(request.data)
        db.session.add(Genre(**genre_data))
        db.session.commit()
        return '', 201


@genre_ns.route('/<int:gid>')
class GenreView(Resource):

    def get(self, gid):
        try:
            genre = db.session.query(Genre).filter(Genre.id == gid).one()
            return director_schema.dump(genre), 200
        except Exception as e:
            return str(e), 404

    def put(self, gid):
        genre = Genre.query.get(gid)
        genre_data = genre_schema.loads(request.data)
        genre.name = genre_data['name']
        db.session.commit()
        return '', 204

    def delete(self, gid):
        genre = Genre.query.get(gid)
        db.session.delete(genre)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
