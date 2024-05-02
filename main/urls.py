from django.urls import path
from main.views import show_dashboard, show_royalties,berlangganan_paket, daftar_paket, riwayat_transaksi, search_results

app_name = 'main'

urlpatterns = [
    path('', show_dashboard, name='show_dashboard'),
    path('cek-royalti/', show_royalties, name='show_royalties'), 
     path('paket/', daftar_paket, name='daftar_paket'),
    path('paket/berlangganan/<int:paket_id>/', berlangganan_paket, name='berlangganan_paket'),
    path('transaksi/', riwayat_transaksi, name='riwayat_transaksi'),
    path('search/', search_results, name='search_results'),

]