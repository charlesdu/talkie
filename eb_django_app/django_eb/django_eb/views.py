import json
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render

from models import *


def index(request):
	movie = Movie.objects.get(mid=9)
	actor = Actor.objects.get(name="Tom Hanks")
	context = RequestContext(request, {'movie': actor})
	return render(request, 'index.html', context)

def search(request):
	if request.method == 'POST':
		post_text = str(request.POST.get('query'))
		response_data = {}
		actor = Actor.objects.get(name=post_text)

		response_data['actor_id'] = actor.aid

		return HttpResponse(
			json.dumps(response_data),
			content_type="application/json"
		)
	else:
		return HttpResponse(
			json.dumps({"nothing to see": "this isn't happening"}),
			content_type="application/json"
		)