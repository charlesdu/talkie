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
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['pwd']
		confirm_password = request.POST['pwd_confirm']
		if password == confirm_password:
			try:
				user = User.objects.create_user(username=username, email=email, password=password)
			except IntegrityError:
				context = RequestContext(request, {'error': "This username already exists. Please try a different one."})
				return render(request, 'sign_up.html', context)
			else:
				user.save()
				new_user = authenticate(username=username, password=password)
				auth_login(request, new_user)
				return redirect('/dashboard')
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
		if movies == None:
			movies = []
		if movies == "Recommendations":
			user_ratings = UserRating.objects.filter(uid=request.user.id)
			mov = [];
			
			for rating in user_ratings:
				movie_rec = recommendation(rating.mid_id, rating.rating)
				for m in movie_rec:
					if m.mid != rating.mid_id:
						mov.append({'mid': m.mid ,
                      'name': m.name,
                      'description': m.description,
                      'year': m.year,
                      'critic_rating': m.critic_rating,
                      'audience_rating': m.audience_rating,
                      'runtime': m.runtime,
                      'image_url': m.image_url
                     })
					if(len(movies)>=20):
						break
				if(len(movies)>=20):
					break
		
				print "len of initial recs: "+str(len(mov))
				if len(mov) < 20:
					number = 20 - len(mov)
					filler = RecRating.objects.order_by('rating')[:number]
					for f in filler:
						mov.append(f.mid)

				movies = json.dumps(mov)
		else:
			movies = json.dumps(movies)
		print movies
		return HttpResponse(
			movies,
			content_type = "application/json"
		)
	else:
		user_ratings = UserRating.objects.filter(uid=request.user.id)
		ratings_by_user = []
		for u in user_ratings:
			ratings_by_user.append(u)

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

		context = RequestContext(request, {'initial_recommendations':movies, 'ratings_by_user':user_ratings, 'username':request.user.username})
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
			movies.append(m)

		print "len of rating recs: "+str(len(movies))
		if len(movies) < 20:
			number = 20 - len(movies)
			filler = RecRating.objects.order_by('rating')[:number]
			for f in filler:
				movies.append(f.mid)

	return HttpResponse(serializers.serialize('json',movies), content_type = "application/json")
