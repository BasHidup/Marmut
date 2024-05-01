from django.urls import path
from albums.views import create_song, edit_album, show_albums, create_album, show_songs

app_name = 'albums'

urlpatterns = [
    path('', show_albums, name='show_albums'),
    path('create-album/', create_album, name='create_album'),
    path('<str:id_album>/songs/', show_songs, name='show_songs'),
    path('<str:id_album>/create-song/', create_song, name='create_song'),
    path('<str:id_album>/edit-album/', edit_album, name='edit_album'),
]