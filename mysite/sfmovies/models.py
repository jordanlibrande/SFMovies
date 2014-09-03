import datetime
from django.utils import timezone
from django.db import models


class DBUpdateHistory(models.Model):
    time_updated = models.DateTimeField('time last refreshed database')
    
    def __str__(self):
        return self.time_updated

        
class Movie(models.Model):
    title = models.CharField(max_length=200) # longest english movie title known has 206 characters
    release_year = models.IntegerField(default=0)
    production_company = models.CharField(max_length=100, null=True)
    distributor = models.CharField(max_length=100, null=True)
    director = models.CharField(max_length=60, null=True)
    writer = models.CharField(max_length=60, null=True)
    
    def __str__(self):
        return self.title
    
    
class Location(models.Model):
    movie = models.ForeignKey(Movie)
    locations = models.CharField(max_length=500) # We get rid of data with no location
    latitude = models.DecimalField(max_digits=7, decimal_places=4, null=True)
    longitude = models.DecimalField(max_digits=7, decimal_places=4, null=True)
    fun_facts = models.CharField(max_length=500, null=True)
    actor_1 = models.CharField(max_length=200, null=True)
    actor_2 = models.CharField(max_length=200, null=True)
    actor_3 = models.CharField(max_length=200, null=True)
    
    def __str__(self):
        return self.locations    