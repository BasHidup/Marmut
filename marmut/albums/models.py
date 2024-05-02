from django.db import models

# Create your models here.
 
class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)

class Podcast(models.Model):
    title = models.CharField(max_length=100)
    creator = models.CharField(max_length=100)

class UserPlaylist(models.Model):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


