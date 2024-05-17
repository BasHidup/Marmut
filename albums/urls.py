from django.urls import path
from albums.views import create_song, show_albums, create_album, show_songs, show_song_detail, delete_song, delete_album
from . import views


app_name = 'albums'

urlpatterns = [
    path('', show_albums, name='show_albums'),
    path('create-album/', create_album, name='create_album'),
    path('<str:id_album>/songs/', show_songs, name='show_songs'),
    path('<str:id_album>/create-song/', create_song, name='create_song'),
    path('song-detail/<str:id_song>/', show_song_detail, name='show_song_detail'),
    path('songs/', views.downloaded_songs, name='downloaded_songs'),
    path('songs/delete/<int:song_id>/', views.delete_downloaded_song, name='delete_downloaded_song'),
    path('<str:id_album>/delete-song/<str:id_song>/', delete_song, name='delete_song'),
    path('<str:id_album>/delete-album/', delete_album, name='delete_album')
]