import json

from models import *
from text2num import text2num


# A list of split terms that a user can ask
action_terms = {
	'show': 1,				# Start of term
	'movies': 1,			# Category of film
	'named': 1,				# Specifies a name for the movie
	'featuring': 1,			# Contains a specific actor
	'directed': 1,			# Contains a specific director
	'in': 1,				# Specifies a year in which it was filmed
	'rating': 1,			# Contains a rating criteria
	'time': 1,				# Specifies a runtime for the movie
}


# A structure for db_query to use when querying the database. These fields will be filled out and passed in before any call to db_query
database_fields = {
	'movie-name': None,
	'movie-description': None,
	'movie-year': None,
	'movie-critic_rating': None,
	'movie-audience_rating': None,
	'movie-runtime': None,
	'actor-name': None,
	'director-name': None,
	'limit': None,
}


# Parses a query into specific terms that can be queried in the database
# Input: a query string
# Returns: object containing table to search, search requirements, and search terms
def parse_query(query):
	db_fields = database_fields.copy()
	query = query.strip().lower()
	query_array = query.split()
	for i in range(len(query_array)):
		if query_array[i] == 'featuring':
			db_fields['actor-name'] = query_array[i+1] + ' ' + query_array[i+2]
	return db_fields


# Queries the database on the input terms
# Input: a terms object containing table to search, search requirements, and search terms
# Returns: object containing all the movies that match the terms, and an optional error term
def db_query(terms):
	movies = {}
	if terms['actor-name'] != None:
		actor = Actor.objects.get(name = terms['actor-name'])
		movieIDs = MovieActor.objects.filter(aid = actor.aid).values_list('mid', flat = True).order_by('mid')
		movies = Movie.objects.filter(mid__in = movieIDs)
	return movies
	

# Takes an array of Movie objects and returns formatted json objects
# Input: array of Movie objects
# Returns: json object containing relevent data for all the movies in the input array
def format_movie_object(movies):
	json = {}
	for movie in movies:
		m = {}
		m['mid'] = movie.mid
		m['name'] = movie.name
		m['description'] = movie.description
		m['year'] = movie.year
		m['critic_rating'] = movie.critic_rating
		m['audience_rating'] = movie.audience_rating
		m['runtime'] = movie.runtime
		m['image_url'] = movie.image_url
		json.append(m)
	print json
	return json.dumps(json)


# Runs NLP on the user's query
# Input: a query string
# Returns: object containing all the movies that match that query, and an optional error term
def run_NLP(query):
	terms = parse_query(query)
	movies = db_query(terms)
	# json = format_movie_object(movies)
	json = movies
	return json