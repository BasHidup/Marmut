from django.urls import path
from authentication.views import login_view, logout, show_start, registrasi, registrasi_pengguna, registrasi_label

app_name = 'authentication'

urlpatterns = [
    path('login/', login_view, name='login_view'),
    path('logout/', logout, name='logout'),
    path('welcome/', show_start, name='show_start'),
    path('register/', registrasi, name='registrasi'),
    path('register/pengguna/', registrasi_pengguna, name='registrasi_pengguna'),
    path('register/label/', registrasi_label, name='registrasi_label')
]