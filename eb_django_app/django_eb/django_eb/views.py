from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render


def index(request):
	context = RequestContext(request, {})
	return render(request, 'index.html', context)