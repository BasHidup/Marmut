# urls.py

from django.urls import path
from podcast.views import daftar_episode

app_name = 'podcast'

urlpatterns = [
    path('play_podcast/<int:id_konten>', daftar_episode, name='daftar_episode'),
]