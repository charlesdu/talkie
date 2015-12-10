import json, re

from models import *
from django.db import connection
from nltk.corpus import stopwords
from text2num import *
from wordnoise import *
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
	'recommendations': None,
	'movie-name': None,
	'movie-description': None,
	'movie-year': None,
	'movie-critic_rating': None,
	'movie-audience_rating': None,
	'movie-rating_type': None,
	'movie-runtime': None,
	'actor-name': None,
	'director-name': None,
	'limit': None,
}

# A set of insignificant words for pre-processing and filtering
word_noise = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselve"]


# Fetchall helper for SQL queries
# Input: a cursor execution
# Output: a dictionary of results
def dictfetchall(cursor):
	columns = [col[0] for col in cursor.description]
	return [
		dict(zip(columns, row))
		for row in cursor.fetchall()
	]


def recommendation(movie_id, r):
	# Find all other users in rec_rating that have rated this movie r stars
	other_users = RecRating.objects.filter(mid = movie_id, rating = r);
	movies = []

	# Find the movies that each of the users above rate 5 stars, and recommend those
	for i in range(len(other_users)):
		user = other_users[i]
		user_movies = RecRating.objects.filter(uid = user.uid, rating = 5)
		
		for j in range(len(user_movies)):
			movies.append(user_movies[j].mid)
			if(len(movies) >= 25):
				break
		if(len(movies) >= 25):
			break

	return movies


# Determines if a query follows the correct structure
# Input: a query string and a pattern string
# Returns: boolean if the query matches
def match(query, pattern):
	# ~ = any number of words [greedy]
	# ! = exactly one word
	# @ = any number of words [lazy]
	# # = any of the actions words
	query = query.strip().lower()
	query += ";"
	pattern = pattern.strip().lower()
	pattern = pattern.replace("~", "(.*)")
	pattern = pattern.replace("!", '([^\s]+)')
	pattern = pattern.replace("@", "(.*?)")
	pattern = pattern.replace("#", "(show me|play|movies|movie|named|name|titled|called|about|featuring|starring|directed by|filmed in|rating|stars|time|;)")
	pattern = pattern.replace(" ", "\s*")
	m = re.match(pattern, query)
	if m:
		print pattern
	return m


# Parses a query into specific terms that can be queried in the database
# Input: a query string
# Returns: object containing table to search, search requirements, and search terms
def parse_query(query):
	# ~ = any number of words [greedy]
	# ! = exactly one word
	# @ = any number of words [lazy]
	# # = any of the actions words
	db_fields = database_fields.copy()
	query = query.strip().lower()
	pattern = ""

	# Recommendations
	pattern = "(@ recommended movies # ~|@ recommended for me # ~|@ my recommendations # ~|@ I would like # ~)"
	if match(query, pattern):
		db_fields['recommendations'] = True
		return db_fields

	# Movie-name
	pattern = "@ (named|name|titled|called) @ # ~"
	if match(query, pattern):
		m = match(query, pattern)
		db_fields['movie-name'] = m.group(3)

	# Movie-description
	pattern = "@ about @ # ~"
	if match(query, pattern):
		m = match(query, pattern)
		description = m.group(2)
		description = filter(lambda w: not w in word_noise,description.split())
		db_fields['movie-description'] = ' '.join(description)

	# Movie-year
	pattern = "@ filmed in ! # ~"
	if match(query, pattern):
		m = match(query, pattern)
		db_fields['movie-year'] = int(m.group(2))

	# Movie-rating
	pattern = "@ rating (of|equal to|greater than|less than) @ # ~"
	if match(query, pattern):
		m = match(query, pattern)
		which = m.group(2)
		number = m.group(3)
		if number.isdigit():
			db_fields['movie-audience_rating'] = int(number) * 20
		else:
			db_fields['movie-audience_rating'] = text2num(number)
		if which == "greater than":
			db_fields['movie-rating_type'] = ">"
		elif which == "less than":
			db_fields['movie-rating_type'] = "<"
		else:
			db_fields['movie-rating_type'] = "="

	# Actor-name
	pattern = "@ (featuring|starring) @ # ~"
	if match(query, pattern):
		m = match(query, pattern)
		db_fields['actor-name'] = m.group(3)

	# Director-name
	pattern = "@ directed by @ # ~"
	if match(query, pattern):
		m = match(query, pattern)
		db_fields['director-name'] = m.group(2)

	# Limit
	pattern = "# ! (movies|movie) ~"
	if match(query, pattern):
		m = match(query, pattern)
		if m.group(2) == "all":
			db_fields['limit'] = None
		elif m.group(2) == "a":
			db_fields['limit'] = 1
		elif m.group(2).isdigit():
			db_fields['limit'] = int(m.group(2))
		else:
			db_fields['limit'] = text2num(m.group(2))

	return db_fields


# Queries the database on the input terms
# Input: a terms object containing table to search, search requirements, and search terms
# Returns: object containing all the movies that match the terms
def db_query(terms):
	pprint(terms)
	# Check to make sure we even have a condition before querying the database
	recall = True
	for term in terms:
		if term != None:
			recall = False
	if recall:
		return None

	# Check to see if its a recommendation
	if terms['recommendations'] == True:
		return "Recommendations"

	movies = {}
	cursor = connection.cursor()
	query = """SELECT DISTINCT M.mid, M.name, M.description, M.year, M.critic_rating, M.audience_rating, M.runtime, M.image_url, D.name AS director FROM Movie M
					INNER JOIN Movie_Actor MA ON M.mid = MA.mid
					INNER JOIN Actor A ON MA.aid = A.aid
					INNER JOIN Movie_Director MD ON M.mid = MD.mid
					INNER JOIN Director D ON MD.did = D.did
					WHERE """
	conditions = []
	if terms['movie-name'] != None:
		conditions.append("M.name LIKE \"%s\"" % terms['movie-name'])
	if terms['movie-description'] != None:
		clause = "("
		descriptors = terms['movie-description'].split()
		for descriptor in descriptors:
			clause += "M.description LIKE \"%%%s%%\" OR " % descriptor
		clause = clause[:-4] + ")"
		conditions.append(clause)
	if terms['movie-year'] != None:
		conditions.append("M.year = %s" % str(terms['movie-year']))
	if terms['movie-audience_rating'] != None:
		conditions.append("M.audience_rating %s %s" % (terms['movie-rating_type'], str(terms['movie-audience_rating'])))
	if terms['actor-name'] != None:
		conditions.append("A.name LIKE \"%s\"" % terms['actor-name'])
	if terms['director-name'] != None:
		conditions.append("D.name LIKE \"%s\"" % terms['director-name'])
	# Build the WHERE conditions
	for condition in conditions:
		query += condition + " AND "
	query = query[:-4]
	# Add the LIMIT
	if terms['limit'] != None:
		query += "LIMIT %s" % str(terms['limit'])
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