import json
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render

from models import *
from utils import *

def index(request):
	context = RequestContext(request, {})
	return render(request, 'index.html', context)

def dashboard(request):
	if request.method == 'POST':
		query = str(request.POST.get('query'))
		movies = run_NLP(query)
		movie = movies[0].name
		print movie

		return HttpResponse(
			json.dumps(movie),
			content_type = "application/json"
		)
	else:
		context = RequestContext(request, {})
		return render(request, 'dashboard.html', context)