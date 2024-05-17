from django.urls import path
from albums.views import *
from albums.views import create_song, show_albums, create_album, show_songs, show_song_detail, delete_song, delete_album
from . import views


app_name = 'albums'

urlpatterns = [
    path('', show_albums, name='show_albums'),
    path('create-album/', create_album, name='create_album'),
    path('<str:id_album>/songs/', show_songs, name='show_songs'),
    path('<str:id_album>/create-song/', create_song, name='create_song'),
    path('song-detail/<str:id_song>/', show_song_detail, name='show_song_detail'),
    # path('edit-song/<str:id_song>/', edit_song, name='edit_song'),
    path('songs/', downloaded_songs, name='downloaded_songs'),
    path('songs/delete/<int:song_id>/', delete_downloaded_song, name='delete_song'),
    path('playlists/', manage_playlists, name='manage_playlists'),
    path('playlists/add/', add_playlist, name='add_playlist'),
    path('playlists/detail/<uuid:playlist_id>/', playlist_detail, name='playlist_detail'),
    path('playlists/<uuid:playlist_id>/edit/', edit_playlist, name='edit_playlist'),
    path('playlists/<uuid:playlist_id>/delete/', delete_playlist, name='delete_playlist'),
    path('playlists/<uuid:playlist_id>/add_song/', add_song_to_playlist, name='add_song_to_playlist'),
    path('songs/play/<uuid:song_id>/', play_song, name='play_song'),
    path('songs/add/<uuid:song_id>/', add_song_to_playlist_with_option, name='add_song_to_playlist_with_option'),
    path('songs/download/<uuid:song_id>/', download_song, name='download_song'),
    path('playlists/<uuid:playlist_id>/delete_song/<uuid:song_id>/', delete_song_from_playlist, name='delete_song_from_playlist'),
    path('playlists/play/<uuid:playlist_id>/', play_user_playlist, name='play_user_playlist'),
    path('playlists/play/<uuid:id_user_playlist>/shuffle_play', shuffle_play, name='shuffle_play'),
    path('songs/', views.downloaded_songs, name='downloaded_songs'),
    path('songs/delete/<int:song_id>/', views.delete_downloaded_song, name='delete_downloaded_song'),
    path('<str:id_album>/delete-song/<str:id_song>/', delete_song, name='delete_song'),
    path('<str:id_album>/delete-album/', delete_album, name='delete_album')
]