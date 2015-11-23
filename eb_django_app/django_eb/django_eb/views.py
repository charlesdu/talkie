import json
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render

from models import *


def index(request):
	context = RequestContext(request, {})
	return render(request, 'index.html', context)

def dashboard(request):
	if request.method == 'POST':
		post_text = str(request.POST.get('query'))
		response_data = {}
		actor = Actor.objects.get(name=post_text)

		response_data['actor_id'] = actor.aid

		return HttpResponse(
			json.dumps(response_data),
		)
	else:
