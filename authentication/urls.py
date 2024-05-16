from django.urls import path
from authentication.views import login_view, logout

app_name = 'authentication'

urlpatterns = [
    path('login/', login_view, name='login_view'),
    path('logout/', logout, name='logout')
]