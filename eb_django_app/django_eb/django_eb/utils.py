import json

from models import *


# Parses a query into specific terms that can be queried in the database
# Input: a query string
# Returns: object containing table to search, search requirements, and search terms
def prepare_for_db(query):
	return None


# Queries the database on the input terms
# Input: a terms object containing table to search, search requirements, and search terms
# Returns: object containing all the movies that match the terms
def db_query(terms):
	return None


# Runs NLP on the user's query
# Input: a query string
# Returns: object containing all the movies that match that query
def parse_query(query):
	terms = prepare_for_db(query)
	movies = db_query(terms)
	return movies