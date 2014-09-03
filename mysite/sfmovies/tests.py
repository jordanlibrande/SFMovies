import unittest
import json

from django.test import Client, TestCase

from sfmovies.updatedb import geocode_and_add_to_db
from sfmovies.models import Location, Movie

def populate_db():
    # Initialize our database with some data
    create_movie_and_location("Test Movie 1", "Golden Gate Bridge") # GPS Coords: (37.8199,-122.4789)
    create_movie_and_location("Test Movie 2", "Crissy Field")
    create_movie_and_location("Test Movie 2", "Grant Street at Pacific Avenue")
    create_movie_and_location("Test Movie 3", "312 Fillmore Street")

def create_movie_and_location(movie_title, locations):
    """
    Creates and saves a Movie with the given title.
    Creates and saves a Location with the given locations and a reference to the Movie.
    """
    data = {
        "title": movie_title,
        "release_year": "0099",
        "locations": locations
    }
    geocode_and_add_to_db(data)
    
class Tests(unittest.TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_views(self):
        """ Run all tests for the view APIs
        We load the data for these tests using the SODA and GOOGLE APIs, to test
        our data-gathering system as well.
        Thus, we do multiple tests on the same sample data to minimize the costly geocoding calls
        """
        populate_db() #add 3 sample movies w/ 4 sample locations to the database
        
        self.bad_urls()
        
        self.locations_view_basic()
        self.locations_view_small_bounds()
        self.locations_view_bad_bounds()
        self.locations_view_title()
        
        self.location_detail_view_basic()
        self.location_detail_view_bad_id()
        
        self.title_autocomplete_view_basic()
        self.title_autocomplete_view_bad_title()
    
    def bad_urls(self):
        # GET requests at non-API urls
        badurls = [
            '/',
            '/sfmovies',
            '/sfmovies/',
            '/sfmovies/services',
            '/sfmovies/services/',
            '/sfmovies/services/randomword'
        ]
        for url in badurls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
    
    def locations_view_basic(self):
        # GET request with super-wide bounds. Check that all four locations were returned.
        response = self.client.get('/sfmovies/services/locations', {'bounds':'35,-130,40,-120'})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content.decode("UTF-8"))
        self.assertEqual(len(data), 4);
        bridgeLocation = {}
        for loc in data:
            self.assertTrue("location_id" in loc)
            self.assertTrue("movie_title" in loc)
            if loc['location_id'] == 1 and loc['movie_title'] == "Test Movie 1":
                bridgeLocation = loc
        self.assertTrue(bridgeLocation != {})
        self.assertTrue("latitude" in bridgeLocation)
        self.assertTrue(abs(bridgeLocation['latitude'] - 37.8199) < 0.001)
        self.assertTrue("longitude" in bridgeLocation)
        self.assertTrue(abs(bridgeLocation['longitude'] - -122.4789) < 0.001)
        
    def locations_view_small_bounds(self):
        # GET request with bounds just around golden gate bridge location. 
        # Check that only that location was returned.
        response = self.client.get('/sfmovies/services/locations', {'bounds':'37.8198,-122.4790,37.8200,-122.4788'})

        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content.decode("UTF-8"))
        self.assertEqual(len(data), 1);
        bridgeLocation = {}
        for loc in data:
            self.assertTrue("location_id" in loc)
            self.assertTrue("movie_title" in loc)
            if loc['location_id'] == 1 and loc['movie_title'] == "Test Movie 1":
                bridgeLocation = loc
        self.assertTrue(bridgeLocation != {})
        self.assertTrue("latitude" in bridgeLocation)
        self.assertTrue(abs(bridgeLocation['latitude'] - 37.8199) < 0.001)
        self.assertTrue("longitude" in bridgeLocation)
        self.assertTrue(abs(bridgeLocation['longitude'] - -122.4789) < 0.001)
    
    def locations_view_bad_bounds(self):
        # GET requests with malformed bounds. 
        # Check that no locations were returned
        badbounds = [
            '',
            'a',
            '153',
            '37.8198,-122.4790,37.8200,-122.4788,',
            '37.8198,-122.4790,37.8200',
            '/'
        ]
        for bounds in badbounds:
            response = self.client.get('/sfmovies/services/locations', {'bounds':bounds})
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content.decode("UTF-8"))
            self.assertEqual(len(data), 0);
            
    def locations_view_title(self):
        # GET request with super-wide bounds but title specified. 
        # Check that correct location returned
        response = self.client.get('/sfmovies/services/locations', 
            {
                'bounds':'35,-130,40,-120',
                'movie_title':'Test Movie 1'
            })

        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content.decode("UTF-8"))
        self.assertEqual(len(data), 1);
        bridgeLocation = {}
        for loc in data:
            self.assertTrue("location_id" in loc)
            self.assertTrue("movie_title" in loc)
            if loc['location_id'] == 1 and loc['movie_title'] == "Test Movie 1":
                bridgeLocation = loc
        self.assertTrue(bridgeLocation != {})
        self.assertTrue("latitude" in bridgeLocation)
        self.assertTrue(abs(bridgeLocation['latitude'] - 37.8199) < 0.001)
        self.assertTrue("longitude" in bridgeLocation)
        self.assertTrue(abs(bridgeLocation['longitude'] - -122.4789) < 0.001)
        
    def location_detail_view_basic(self):
        # Make all four valid location_detail queries
        for i in range(1,5):
            response = self.client.get('/sfmovies/services/location_detail', {'location_id':i})
            self.assertEqual(response.status_code, 200)
        
            data = json.loads(response.content.decode("UTF-8"))
            loc = Location.objects.get(pk=i)
            movie = loc.movie
            
            self.assertTrue(data['location_id'] == loc.id)
            self.assertTrue(data['Title'] == movie.title)
            self.assertTrue(data['Release Year'] == movie.release_year)
            self.assertTrue(data["Production Company"] == movie.production_company)
            self.assertTrue(data["Distributor"] == movie.distributor)
            self.assertTrue(data["Director"] == movie.director)
            self.assertTrue(data["Writer"] == movie.writer)
            self.assertTrue(data["Locations"] == loc.locations)
            self.assertTrue(data["Latitude"] == float(loc.latitude))
            self.assertTrue(data["Longitude"] == float(loc.longitude))
            self.assertTrue(data["Fun Facts"] == loc.fun_facts)
            self.assertTrue(data["Actor 1"] == loc.actor_1)
            self.assertTrue(data["Actor 2"] == loc.actor_2)
            self.assertTrue(data["Actor 3"] == loc.actor_3)
    
    def location_detail_view_bad_id(self):
        # Make a variety of bad location_detail queries.
        # Expected response: an empty dictionary in all cases
        bad_ids = [
            '',
            ',',
            ', ',
            '.',
            '0.0',
            '0',
            '40',
            ' ',
            '3.1',
            '3.0',
            '3.',
            'a',
            '/',
            '1,1',
            '0x1'
        ]
        for id in bad_ids:
            response = self.client.get('/sfmovies/services/location_detail', {'location_id':id})
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content.decode("UTF-8"))
            self.assertTrue(data == {})
            
    def title_autocomplete_view_basic(self):
        title = "Test MoVIe "
        # Test every prefix substring. They should all match all three test movies.
        # Also tests that lowercasing is working as expected
        for i in range(len(title) + 1):
            t = title[:i]
            response = self.client.get('/sfmovies/services/title_autocomplete', {'term':t})
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content.decode("UTF-8"))
            self.assertEqual(len(data), 3)
            for mov_title in data:
                self.assertTrue(
                    (mov_title['value'] == "Test Movie 1" and mov_title['label'] == "Test Movie 1") or
                    (mov_title['value'] == "Test Movie 2" and mov_title['label'] == "Test Movie 2") or
                    (mov_title['value'] == "Test Movie 3" and mov_title['label'] == "Test Movie 3")
                )
            
        title = "Test Movie 1"
        # This prefix string should only match "Test Movie 1"
        response = self.client.get('/sfmovies/services/title_autocomplete', {'term':title})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode("UTF-8"))
        self.assertEqual(len(data), 1)
        self.assertTrue(data[0]['value'] == "Test Movie 1" and data[0]['label'] == "Test Movie 1")
    
    def title_autocomplete_view_bad_title(self):
        bad_titles = [
            'x',
            '1',
            ' ',
            '@',
            '$',
            'Test Movie 4',
            'Test Movie 1 ',
            '"Test Movie 1"'
        ]
        for title in bad_titles:
            response = self.client.get('/sfmovies/services/title_autocomplete', {'term':title})
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content.decode("UTF-8"))
            self.assertTrue(data == [])