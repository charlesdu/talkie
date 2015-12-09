import json, re

from models import *
from django.db import connection
from text2num import *
from pprint import pprint

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

# Fetchall helper for SQL queries
def dictfetchall(cursor):
	columns = [col[0] for col in cursor.description]
	return [
		dict(zip(columns, row))
		for row in cursor.fetchall()
	]


def recommendation(movie_id):
	#Find all other users in rec_rating that have rated this movie 5 stars
	other_users = RecRating.objects.filter(mid = movie_id, rating = 5);

	#Find the movies that each of the users above rate 5 stars, and recommend those
	for user in other_users:
		movies = RecRating.objects.filter(uid = user.uid, rating = 5);


# Determines if a query follows the correct structure
# Input: a query string and a pattern string
# Returns: boolean if the query matches
def match(query, pattern):
	# ~ = any number of words [greedy]
	# ! = exactly one word
	# @ = any number of words [lazy]
	query = query.strip().lower()
	pattern = pattern.strip().lower()
	pattern = pattern.replace("~", "(.*)")
	pattern = pattern.replace("!", '([^\s]+)')
	pattern = pattern.replace("@", "(.*?)")
	pattern = pattern.replace(" ", "\s*")
	print pattern
	return re.match(pattern, query)


# Parses a query into specific terms that can be queried in the database
# Input: a query string
# Returns: object containing table to search, search requirements, and search terms
def parse_query(query):
	db_fields = database_fields.copy()
	query = query.strip().lower()
	# Show me [number] movies
	if match(query, "Show me ! movies ~"):
		m = match(query, "Show me ! movies ~")
		if m.group(1) == "all":
			db_fields['limit'] = None
		elif m.group(1).isdigit():
			db_fields['limit'] = int(m.group(1))
		else:
			db_fields['limit'] = text2num(m.group(1))
	# Show me movies featuring [actors]
	if match(query, "Show me @ movies featuring ~"):
		m = match(query, "Show me @ movies featuring ~")
		db_fields['actor-name'] = m.group(2)
	return db_fields


# Queries the database on the input terms
# Input: a terms object containing table to search, search requirements, and search terms
# Returns: object containing all the movies that match the terms, and an optional error term
def db_query(terms):
	pprint(terms)
	movies = {}
	cursor = connection.cursor()
	query = """SELECT DISTINCT M.mid, M.name, M.description, M.year, M.critic_rating, M.audience_rating, M.runtime, M.image_url FROM Movie M
					INNER JOIN Movie_Actor MA ON M.mid = MA.mid
					INNER JOIN Actor A ON MA.aid = A.aid
					INNER JOIN Movie_Director MD ON M.mid = MD.mid
					INNER JOIN Director D ON MD.did = D.did"""
	if terms['actor-name'] != None:
		query += " WHERE A.name LIKE \"%s\"" % terms['actor-name']
	if terms['limit'] != None:
		query += " LIMIT %s" % str(terms['limit'])
	print query
	cursor.execute(query)
	movies = dictfetchall(cursor)
	return movies
	

# Runs NLP on the user's query
# Input: a query string
# Returns: object containing all the movies that match that query, and an optional error term
def run_NLP(query):
	terms = parse_query(query)
	movies = db_query(terms)
	return movies