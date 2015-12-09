import json
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db import IntegrityError
from pprint import pprint
from django.core import serializers

from models import *
from utils import *

global_user=None;

def logout(request):
	auth_logout(request)
	global_user = None;
	context = RequestContext(request, {})
	return redirect('/')

def login(request):
	if request.method == 'POST':
		user = authenticate(username=request.POST['username'], password=request.POST['pwd'])
		if user is not None:
			if user.is_active:
				auth_login(request, user)
				return redirect('/dashboard')
			else:
				context = RequestContext(request, {'error': "This account has been disabled. Please try a different account."})
				return render(request, 'login.html', context)
		else:
			context = RequestContext(request, {'error': "Username and password combination not found. Please try again."})
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
				context = RequestContext(request, {'error': "This username already exists. Please try a different one."})
				return render(request, 'sign_up.html', context)
			else:
				user.save()
				context = RequestContext(request, {})
				return redirect('/dashboard ')
		else:
			context = RequestContext(request, {'error': "The passwords do not match. Please try again."})
			return render(request, 'sign_up.html', context)        
	else:
		context = RequestContext(request, {})
		return render(request, 'sign_up.html', context)

def dashboard(request):
	if not request.user.is_authenticated():
		return redirect('/')
	if request.method == 'POST':
		query = str(request.POST.get('query'))
		movies = run_NLP(query)
		return HttpResponse(
			json.dumps(movies),
			content_type = "application/json"
		)
	else:
		context = RequestContext(request, {})
		return render(request, 'dashboard.html', context)
