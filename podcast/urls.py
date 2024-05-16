# urls.py

from django.urls import path
from podcast.views import play_podcast, list_podcast, lihat_episode, home_podcast

app_name = 'podcast'

urlpatterns = [
    path('', home_podcast, name='home_podcast'),
    path('<str:id>/', play_podcast, name='play_podcast'),
    path('list/', list_podcast, name='list_podcast'),
    path('list/<str:id>/', lihat_episode, name='lihat_episode'),
]