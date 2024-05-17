from django.shortcuts import render, redirect, get_object_or_404
from .models import Paket, Transaksi
from django.contrib import messages
from django.db import connection

# Create your views here.
def has_logged_in(request):
    print(request.session['email'])
    print(request.session['roles'])
    if request.session['email'] == 'not found' or request.session['roles'] == 'not found':
        return False
    
    return True

def show_dashboard(request):
    
    return render(request, 'dashboardlabel.html')

def show_royalties(request):
    if not has_logged_in(request):
        return redirect('authentication:login_view')
    
    royalties = []
    email = request.session['email']

    with connection.cursor() as cursor:
        query = """
            SELECT DISTINCT
                k.judul AS song_title,
                a.judul AS album_title,
                s.total_play,
                s.total_download,
                (s.total_play * p.rate_royalti) AS total_royalty,
                u.email AS owner_email
            FROM 
                ROYALTI r
            JOIN 
                SONG s ON r.id_song = s.id_konten
            JOIN 
                KONTEN k ON s.id_konten = k.id
            JOIN 
                ALBUM a ON s.id_album = a.id
            JOIN 
                PEMILIK_HAK_CIPTA p ON r.id_pemilik_hak_cipta = p.id
            LEFT JOIN 
                ARTIST ar ON ar.id_pemilik_hak_cipta = p.id
            LEFT JOIN 
                SONGWRITER sw ON sw.id_pemilik_hak_cipta = p.id
            LEFT JOIN 
                LABEL l ON l.id_pemilik_hak_cipta = p.id
            LEFT JOIN 
                AKUN u ON u.email = ar.email_akun OR u.email = sw.email_akun OR u.email = l.email
        """
        cursor.execute(query)
        royalty_results = cursor.fetchall()

    for row in royalty_results:
        if row[5] == email:
            royalties.append({
                'song_title': row[0],
                'album_title': row[1],
                'total_play': row[2],
                'total_download': row[3],
                'total_royalty': row[4],
                'owner_email': row[5],
            })

    context = {
        'royalties':royalties,
    }

    return render(request, 'cek_royalti.html', context)


def daftar_paket(request):
    pakets = Paket.objects.all()
    return render(request, 'daftar_paket.html', {'pakets': pakets})

def berlangganan_paket(request, paket_id):
    paket = get_object_or_404(Paket, id=paket_id)
    if request.method == 'POST':
        Transaksi.objects.create(
            user=request.user,
            paket=paket,
            metode_pembayaran=request.POST.get('metode_pembayaran')
        )
        messages.success(request, 'Berhasil berlangganan paket!')
        return redirect('riwayat_transaksi')
    return render(request, 'berlangganan_paket.html', {'paket': paket})

def riwayat_transaksi(request):
    transaksi = Transaksi.objects.filter(user=request.user)
    return render(request, 'riwayat_transaksi.html', {'transaksi': transaksi})
