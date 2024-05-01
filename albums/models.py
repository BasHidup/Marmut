from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class DownloadedSong(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloaded_songs')
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    download_date = models.DateField()

    def __str__(self):
        return f"{self.title} by {self.artist}"
