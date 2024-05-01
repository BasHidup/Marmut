from django.urls import path
from main.views import show_dashboard, show_royalties

app_name = 'main'

urlpatterns = [
    path('', show_dashboard, name='show_dashboard'),
    path('cek-royalti/', show_royalties, name='show_royalties'), 
]