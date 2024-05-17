# urls.py

from django.urls import path
from podcast.views import *
app_name = 'podcast'

urlpatterns = [
    path('home/', home_podcast, name='home_podcast'),
    path('home/<str:id>/', play_podcast, name='play_podcast'),
    
    path('list/', list_podcast, name='list_podcast'),
    path('list/<str:id>/', lihat_episode, name='lihat_episode'),
    path('list/tambah_episode/<str:id>', tambah_episode, name='tambah_episode'),
    path('form_tambah_episode/<str:id>', form_tambah_episode, name='form_tambah_episode'),
    path('tambah_podcast/<str:email>', tambah_podcast, name='tambah_podcast'),
    path('form_tambah_podcast/<str:email>', form_tambah_podcast, name='form_tambah_podcast'),

    path('delete_episode/<str:id_episode>/', delete_episode, name='delete_episode'),
    path('delete_podcast/<str:id>/', delete_podcast, name='delete_podcast'),



    #path('list/edit_episode/<str:id>', edit_episode, name='edit_episode'),
    #path('form_edit_episode/<str:id>', form_edit_episode, name='form_edit_episode'),
    #path('edit_podcast/<str:id>', edit_podcast, name='edit_podcast'),
    #path('form_edit_podcast/<str:id>', form_edit_podcast, name='form_edit_podcast'),

]