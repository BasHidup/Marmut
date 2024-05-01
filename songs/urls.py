from django.urls import path
from songs.views import show_detail, edit_song

app_name = 'songs'

urlpatterns = [
    path('<str:id_song>/detail/', show_detail, name='show_detail'),
    path('<str:id_song>/edit/', edit_song, name='edit_song'),
]