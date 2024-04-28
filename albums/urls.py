from django.urls import path
from albums.views import show_albums

app_name = 'albums'

urlpatterns = [
    path('', show_albums, name='show_albums'),
]