from neomodel import StructuredNode, StringProperty, IntegerProperty, FloatProperty, RelationshipTo, RelationshipFrom, DateProperty


class Movie(StructuredNode):
    movie_id = StringProperty()
    imdb_id = StringProperty()
    title = StringProperty()
    tagline = StringProperty()
    overview = StringProperty()
    budget = IntegerProperty()
    revenue = IntegerProperty()
    release_date = DateProperty()
    vote_avg = FloatProperty()
    vote_count = IntegerProperty()
    directed_by = RelationshipFrom('Person', "DIRECTED")
    actors = RelationshipFrom('Person', "ACTED_IN")
    genres = RelationshipTo('Genre', "BELONGS_TO_GENRE")


class Person(StructuredNode):
    person_id = StringProperty()
    imdb_id = StringProperty()
    name = StringProperty()
    birthday = DateProperty()
    deathday = DateProperty()
    biography = StringProperty()
    directed = RelationshipTo('Movie', "DIRECTED")
    acted_in = RelationshipTo('Movie', "ACTED_IN")


class Genre(StructuredNode):
    genre_id = StringProperty()
    name = StringProperty()


