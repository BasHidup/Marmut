from django.urls import path
from authentication.views import login_view, logout, show_start

app_name = 'authentication'

urlpatterns = [
    path('login/', login_view, name='login_view'),
    path('logout/', logout, name='logout'),
    path('welcome/', show_start, name='show_start'),
]