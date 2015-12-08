import json
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render, render_to_response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.db import IntegrityError
from pprint import pprint
from django.core import serializers

from models import *
from utils import *

def login(request):
	if request.method == 'POST':
		user = authenticate(username=request.POST['username'], password=request.POST['pwd'])
		if user is not None:
			if user.is_active:
				auth_login(request, user)
				context = RequestContext(request, {})
				return render(request, 'dashboard.html', context)
			else:
				context = RequestContext(request, {'error_message': "This account has been disabled. Please try a different account."})
				return render(request, 'login.html', context)
		else:
			context = RequestContext(request, {'error_message': "Username and password combination not found. Please try again."})
			return render(request, 'login.html', context)
	else:
		context = RequestContext(request, {})
		return render(request, 'login.html', context)

def sign_up(request):
	if request.method == 'POST':
		if request.POST['pwd'] == request.POST['pwd_confirm']:
			try:
				user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['pwd'])
			except IntegrityError:
				context = RequestContext(request, {'error_message': "This username already exists. Please try a different one."})
				return render(request, 'sign_up.html', context)
			else:
				user.save()
				context = RequestContext(request, {})
				return render(request, 'dashboard.html', context)
		else:
			context = RequestContext(request, {'error_message': "The passwords do not match. Please try again."})
			return render(request, 'sign_up.html', context)        
	else:
		context = RequestContext(request, {})
		return render(request, 'sign_up.html', context)

def dashboard(request):
	if request.method == 'POST':
		query = str(request.POST.get('query'))
		movies = run_NLP(query)
		movie = movies[0].name
		print pprint(vars(movies[0]))
		print type(movies)

		return HttpResponse(
			serializers.serialize('json', movies),
			content_type = "application/json"
		)
	else:
		context = RequestContext(request, {})
		return render(request, 'dashboard.html', context)
