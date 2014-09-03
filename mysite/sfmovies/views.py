import json
from decimal import *

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings

from sfmovies.models import Movie, Location
    
def locations(request):
    try:
        bounds = [Decimal(x) for x in request.GET['bounds'].split(',')]
        locs = Location.objects.all()
        if 'movie_title' in request.GET:
            locs = locs.filter(movie__title__startswith=request.GET['movie_title'])
        locs = locs.filter( 
            latitude__gte=bounds[0],
            latitude__lte=bounds[2],
            longitude__gte=bounds[1],
            longitude__lte=bounds[3]
        ) [:settings.NUM_LOCATIONS_TO_RETURN]
        data = []
        for loc in locs:
            data.append({
                "location_id" : loc.id,
                "movie_title" : loc.movie.title,
                "latitude" : float(loc.latitude),
                "longitude" : float(loc.longitude)
            })
        data = json.dumps(data)
    except:
        data = json.dumps([])
    if 'callback' in request.GET:
        # Format for jsonp
        data = '{0}({1})'.format(request.GET['callback'], data) 
    return HttpResponse(data, content_type='application/json')
    
def location_detail(request):
    try:
        loc_id = request.GET['location_id']
        loc = get_object_or_404(Location, pk=loc_id)
        movie = Movie.objects.get(pk=loc.movie_id)
        
        data = json.dumps({
            "location_id":loc.id, 
            "Title":movie.title,
            "Release Year":movie.release_year,
            "Production Company":movie.production_company,
            "Distributor":movie.distributor,
            "Director":movie.director,
            "Writer":movie.writer,
            "Locations":loc.locations,
            "Latitude":float(loc.latitude),
            "Longitude":float(loc.longitude),
            "Fun Facts":loc.fun_facts,
            "Actor 1":loc.actor_1,
            "Actor 2":loc.actor_2,
            "Actor 3":loc.actor_3,
        })
    except:
        data = json.dumps({})    
        
    if 'callback' in request.GET:
        # Format for jsonp
        data = '{0}({1})'.format(request.GET['callback'], data)
    return HttpResponse(data, content_type='application/json')

def title_autocomplete(request):
    try:
        term = request.GET['term']
        suggestedMovies = Movie.objects.filter(title__startswith=term)[:settings.NUM_AUTOCOMPLETE_SUGGESTIONS]
    except:
        suggestedMovies = Movie.objects.all()[:settings.NUM_AUTOCOMPLETE_SUGGESTIONS]
        
    data = json.dumps([{'label':m.title, 'value':m.title} for m in suggestedMovies])
    if 'callback' in request.GET:
        # Format for jsonp
        data = '{0}({1})'.format(request.GET['callback'], data)
    return HttpResponse(data, content_type='application/json')
    
    
    
    
    
    
    