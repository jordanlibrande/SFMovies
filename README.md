#SFMovies
UberFarmer's application for the [Uber Coding Challenge](https://github.com/uber/coding-challenge-tools). 

Project: **SF Movies**    (this may be obvious...)
## Usage

Before you start, set these two environment variables: `DJANGO_SFMOVIES_SECRET_KEY` and `GOOGLE_API_KEY`. Use Django to generate you a new random secret key, and use your own Google API Key.

Get your database into shape with the command `python manage.py syncdb` , run `sfmovies.updatedb.update_db_if_old()` to fill the database with data, and then run the webserver locally using the command `python manage.py runserver`. Once it's up and running, you can point the front-end to your new SFMovies API Endpoint.

Enjoy exploring San Francisco's rich motion picture history with **SFMovies**!

## SFMovies RESTful API Documentation

SFMovies has three API calls, all of which return JSON[P] data. They are located under `/sfmovies/services/`.

###`GET locations`
* Required parameter: `bounds=latlo,lnglo,lathi,lnghi` where `latlo` is the West boundary, `lathi` is the East boundary, `lnglo` is the South boundary, and `lnghi` is the North boundary.
* Optional parameter: `title=x` where `x` is a movie title.
* Returns information about up to 50 movie locations within the specified region. If the `title` option is set, locations from that movie will be returned.
Example API call:
```
GET examplehost/sfmovies/services/locations?bounds=37.702607%2C-122.516062%2C37.835453%2C-122.338049&movie_title=The+Assassination+of+Richard+Nixon
```
Example API response:
```
[
  {"latitude": 37.7976, "longitude": -122.4059, "location_id": 727, "movie_title": "The Assassination of Richard Nixon"},
  {"latitude": 37.7889, "longitude": -122.4131, "location_id": 728, "movie_title": "The Assassination of Richard Nixon"}
]
```

###`GET location_detail`
* Required parameter: `location_id=id` where `id` is the unique id of a location. Location ids can be discovered through the `GET sfmovies/services/locations` call.
* Returns information about that location
Example API call:
```
GET examplehost/sfmovies/services/location_detail?location_id=728
```
Example API response:
```
{"Actor 1": "Sean Penn", "Longitude": -122.4131, "Writer": "Niels Mueller & Kevin Kennedy", "Actor 3": null, "Production Company": "Anhelo Productions", "Fun Facts": null, "Actor 2": "Naomi Watts", "Title": "The Assassination of Richard Nixon", "Locations": "766 Sutter Street", "Release Year": 2004, "Distributor": "THINKFilm", "Director": "Niels Mueller", "Latitude": 37.7889, "location_id": 728}
```

###`GET title_autocomplete`
* Required parameter: `term=x` where `x` is the beginning of a movie title. `term` was chosen as the parameter name for easy compatability with the jQueryUI autocomplete widget.
* Returns up to 5 movie titles matching the provided beginning of title.
Example API call:
```
GET examplehost/sfmovies/services/title_autocomplete?term=f
```
Example API response:
```
[  
  {  "label":"Family Plot",  "value":"Family Plot" },
  {  "label":"Fat Man and Little Boy", "value":"Fat Man and Little Boy" },
  {  "label":"Fearless", "value":"Fearless" },
  {  "label":"Final Analysis", "value":"Final Analysis" },
  {  "label":"Flower Drum Song", "value":"Flower Drum Song" }
]
```

## Project Discussion
####Technical Track:
Primarily back-end. (Although I also created a reasonable but not super-polished front-end).

####Assumptions:
* The user wants to pan and zoom the map around San Francisco and see where movie scenes have been shot
* The user wants to be able to tap on a location and get more information about the movie and scene that was shot there.
* Returning 50 locations at a time is a reasonable upper limit -- A front-end could always choose to display fewer of them.
* Returning 5 autocomplete suggestions at a time is a reasonable number.
* Movie title will be the most common parameter users will want to filter by.

####Technical Choices + Experience:
*Note: Prior to this project, I have had almost no experience with web development. While I tried to choose technologies that would let me accomplish the job, I leaned toward widely-adopted technologies that I felt I should have experience with.*

######Back-end:
* *[Python 3.4](https://www.python.org/)*: I chose Python because I was proficient with it and wanted to use Django as my web framework. I prefer Python 3 when I don't have to care about backwards-compatibility (though I didn't end up using very many Python 3 features).
  * Previous experience: I was already fluent in Python before this project.
* *[Django](https://www.djangoproject.com/)*: I chose Django as my back-end web framework because it was well-developed, well-documented, and widely used. In addition, it was recommended by one of my friends and it has a built-in testing framework. Lastly, I wanted to learn it anyway. I knew from the start there was a chance it would be more complicated and heavy than was necessary. 
  * Previous experience: None (no experience with any web framework)
* *SQLite3*: Default database for Django. Didn't see any reason to switch.
  * Previous experience: Some with other databases, none with SQLite. 
* *[Requests](http://docs.python-requests.org/en/latest/)*: I used this to simplify HTTP requests from Python.
  * Previous experience: None
* *[Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding/)*: The obvious choice to convert from locations into GPS coordinates.
  * Previous experience: None
* *[SFData SODA API](https://data.sfgov.org/)*: I chose to collect the data through their JSON web API so it would be easy to update my database if SFData's movies database was updated.
  * Previous experience: None
* *[Amazon AWS](aws.amazon.com)*: I chose this for my back-end hosting because I was sure it would be sufficient and I wanted experience using it. 
  * Previous experience: None
* *Apache HTTP Server*: Seemed like a common server choice with Django.
  * Previous experience: None 

######Front-end:
* *HTML/Javascript/CSS*: The only choice for modern web development. As I was planning to make a bare-bones front-end experience (and I wanted more experience with these technologies) I wrote these straight (using some snippets from the web) instead of using a front-end framework.
  * Previous experience: Minimal experience with HTML, Minimal experience with Javascript (no experience with Javascript on the web), Minimal experience with CSS.
* *[jQuery](jquery.com)*: I chose to use jQuery to simplify my client-side scripting (in particular AJAX calls). It looked to be widely-adopted and well-supported.
  * Previous experience: None
* *[jQuery UI](jqueryui.com)*: I used this library for their autocomplete widget, which did all of the hard work for me. I chose to get my widget from jQuery UI because it seemed widely-adopted and well-supported. 
  * Previous experience: None 
* *[Google Maps Javascript API](https://developers.google.com/maps/documentation/javascript/)*: I wanted to plot things on a map. This seemed like the choice.
  * Previous experience: None
* [GitHub](github.com): front-end hosting
  * Previous experience: None 

######Misc:
* [GitHub](github.com): source code hosting + version control
  * Previous experience: None
* Zero to minimal experience with: REST/RESTful APIs, HTTP requests

####Trade-Offs and Future Work:
* As suspected, Django was too complicated in areas I didn't care about (e.g. templating and formatting HTML, site administration, authentication), and didn't provide enough support for some things I wanted to do (sending HTTP GET requests, processing JSON, sending JSON and JSONP responses). If I was doing this project over again, I would try a different back-end framework or use a Django extension designed with REST/JSON in mind.
* I could have devoted more time cleaning up the front-end, adding more styles, formatting the location detail text, and using a more intelligent algorithm for marker updates.
* I would add more options to the back-end API. One example: letting users choose the number of locations they want info about and specifying data offsets (like the SODA API).
* I would spend more time on the back-end tests.
* I would come up with a smarter way to update my database using the DataSF site than by wiping my local database and starting over
* Some of the back-end code could be modularized and refactored. For example, optionally turning JSON responses into JSONP could be less repetitive.
* Stretch goals/features: 
  * Links to imdb pages of the movies
  * Which scene of the movie took place in that location (with start+end times)? (super-strech goal: show the actual scene from the movie)
  * Fancier search filtering
  * Expand beyond SF
  * Geolocalization for better mobile app use
  * Monetization (Movie ads!??!)
  * API Keys

####Boilerplate Code:
Files without [much] contribution from me:
```
mysite/
    manage.py
    mysite/
        __init__.py
        settings.py
        urls.py
        wsgi.py
    sfmovies/
        admin.py
    templates/
        admin/
            base_site.html
```

####[LinkedIn Profile](https://www.linkedin.com/in/jlibrande)
