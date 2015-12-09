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
		user_ratings = UserRating.objects.filter(uid=request.user.id)
		print "number of user ratings: "+str(len(user_ratings))
		movies = [];
		for rating in user_ratings:
			movie_rec = recommendation(rating.mid_id, rating.rating)
			for m in movie_rec:
				if m.mid != rating.mid_id:
					movies.append(m)
				if(len(movies)>=20):
					break
			if(len(movies)>=20):
				break
		
		print "len of initial recs: "+str(len(movies))
		if len(movies) < 20:
			number = 20 - len(movies)
			filler = RecRating.objects.order_by('rating')[:number]
			for f in filler:
				movies.append(f.mid)

		context = RequestContext(request, {'initial_recommendations':movies})
		return render(request, 'dashboard.html', context)

def rate_movie(request):
	if request.method == 'POST':
		print request.POST.get('m')
		print request.POST.get('rating')
		print request.user.id
		movie = Movie.objects.get(mid = request.POST.get('m'))
		user = AuthUser.objects.get(id = request.user.id)
		ur = UserRating.objects.filter(uid_id=request.user.id, mid=movie)
		if ur.exists():
			ur = UserRating.objects.get(uid_id=request.user.id, mid=movie)
			ur.rating = request.POST.get('rating')
		else:
			ur = UserRating(uid_id=request.user.id, mid=movie, rating=request.POST.get('rating'))
		ur.save()
		movie_recs = recommendation(movie.mid, request.POST.get('rating'))
		movies = [];
		for m in movie_recs:
			print "movie rec: "+str(m.mid)
			movies.append(m)
	return HttpResponse(serializers.serialize('json',movies), content_type = "application/json")
