from django.conf.urls import patterns, url

from sfmovies import views

urlpatterns = patterns('',
    url(r'^services/locations$', views.locations, name='locations'),
    url(r'^services/location_detail$', views.location_detail, name='location detail'),
    url(r'^services/title_autocomplete$', views.title_autocomplete, name='title autocomplete'),
)