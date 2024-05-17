from django.urls import path
from main.views import show_dashboard, show_homepage, show_royalties,berlangganan_paket, daftar_paket, riwayat_transaksi, search

app_name = 'main'

urlpatterns = [
    path('', show_dashboard, name='show_dashboard'),
    path('home', show_homepage, name='show_homepage'),
    path('cek-royalti/', show_royalties, name='show_royalties'), 
    path('paket/', daftar_paket, name='daftar_paket'),
    path('paket/berlangganan/<str:jenis_paket>/', berlangganan_paket, name='berlangganan_paket'),
    path('transaksi/', riwayat_transaksi, name='riwayat_transaksi'),
    path('search/', search, name='search'),
]