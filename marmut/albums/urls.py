from django.urls import path
from albums.views import create_song, edit_album, show_albums, create_album, show_songs, show_song_detail, edit_song, search_results


app_name = 'albums'

urlpatterns = [
    path('', show_albums, name='show_albums'),
    path('create-album/', create_album, name='create_album'),
    path('<str:id_album>/songs/', show_songs, name='show_songs'),
    path('<str:id_album>/create-song/', create_song, name='create_song'),
    path('<str:id_album>/edit-album/', edit_album, name='edit_album'),
    path('song-detail/<str:id_song>/', show_song_detail, name='show_song_detail'),
    path('edit-song/<str:id_song>/', edit_song, name='edit_song'),
    path('search/', search_results, name='search_results'),

]