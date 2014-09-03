import requests
import json
import datetime
import time

from django.utils import timezone
from django.conf import settings

from sfmovies.models import Movie, Location, DBUpdateHistory

SFMOVIES_API_ENDPOINT = "http://data.sfgov.org/resource/yitu-d5am.json"
GOOGLE_GEOCODING_ENDPOINT = "https://maps.googleapis.com/maps/api/geocode/json"

"""
These functions can be called to populate the database using the SODA data.
Currently, the expected way to refresh the database data is to manually run
update_db_if_old().
"""

def update_db_if_old():
    if (len(DBUpdateHistory.objects.all()) == 0):
        update_db()
    elif (timezone.now() - DBUpdateHistory.objects.all().
            order_by('-time_updated')[0].time_updated >= settings.DB_TIMEOUT):
        update_db()
    else:
        print("database already up to date!")
        
def update_db():
        #re-populate our database using the SODA JSON API
        #link to data: https://data.sfgov.org/Arts-Culture-and-Recreation-/Film-Locations-in-San-Francisco/yitu-d5am
        
        print("updating db")
        print("deleting all records from existing Movie and Location objects")
        Movie.objects.all().delete()
        Location.objects.all().delete()
        
        print("querying our data")
        i = 0
        while(True):
            payload = {'$limit': 1000, '$offset': i*1000}
            r = requests.get(SFMOVIES_API_ENDPOINT, params=payload)
            data = r.json()
            print("gathered first", len(data), "records")
            if len(data) == 0:
                # We've gathered all the records.
                break
            for d in data:
                geocode_and_add_to_db(d)
            i += 1
        # We have finished updating our database. Record the time.
        now = timezone.now()
        print("Database update complete. Recording update time of:", now) 
        DBUpdateHistory.objects.create(time_updated=now)
        
def geocode_and_add_to_db(d):
    """
    d is a python dictionary with the following allowed keys:
    {
      "title" : "Tucker: The Man and His Dreams",
      "actor_1" : "Jeff Bridges",
      "locations" : "City Hall",
      "fun_facts" : "The dome of SF's City Hall is almost a foot taller than that of the US Capitol Building. In 1954, Joe DiMaggio and Marilyn Monroe married at the Beaux Arts-style building.",
      "release_year" : "1988",
      "production_company" : "Lucasfilm",
      "distributor" : "Paramount Pictures",
      "actor_2" : "Joan Allen",
      "writer" : "Arnold Schulman",
      "director" : "Francis Ford Coppola",
      "actor_3" : "Ellyn Burstyn"
    }
    'title', 'locations', and 'release_year' are required keys for us to enter the data into our database
    
    This function creates and adds the Movie object to our db if it is newly seen.
    It creates a Location object and adds it to the db if it could be successfully geocoded.
    """
    # We don't need to track movies or locations with no location.
    if 'title' not in d or 'locations' not in d or 'release_year' not in d:
        print("data incomplete -- nothing added to database")
        return
    
    # Create new Movie and Location records for our data
    obj, created = Movie.objects.get_or_create(
        title=d['title'],
        release_year=d['release_year']
        )
    if created:
        if 'production_company' in d:
            obj.production_company = d['production_company']
        if 'distributor' in d:
            obj.distributor = d['distributor']
        if 'director' in d:
            obj.director = d['director']
        if 'writer' in d:
            obj.writer = d['writer']
        obj.save()
        
    loc = Location(movie_id=obj.id, locations=d['locations'])
    if 'fun_facts' in d:
        loc.fun_facts = d['fun_facts']
    if 'actor_1' in d:
        loc.actor_1 = d['actor_1']
    if 'actor_2' in d:
        loc.actor_2 = d['actor_2']
    if 'actor_3' in d:
        loc.actor_3 = d['actor_3']
    
    # Use Google Maps api to attempt to get a latitute & longitude based on the location description    
    time.sleep(0.1) # Don't overload Google's API quota
    payload = {
        'key':settings.GOOGLE_API_KEY, 
        'address':loc.locations, 
        'components':'locality:San Francisco'
    }
    geo = requests.get(GOOGLE_GEOCODING_ENDPOINT, params=payload)
    locationData = geo.json()
    print("Geocoding", loc.locations, "for", loc.movie.title)
    if len(locationData) >= 1 and locationData['status'] == 'OK':
        l = locationData['results'][0]['geometry']['location']
        loc.latitude = l['lat']
        loc.longitude = l['lng']
        print("Geocoding successful:", "lat:", loc.latitude, "lng:", loc.longitude)
        loc.save() # Only save locations we successfully geocoded.
    else:
        print("Geocoding failed with error:", locationData['status'])
    return