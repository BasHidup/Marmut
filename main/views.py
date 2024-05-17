from django.http import HttpResponse
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
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    context = {}
    if 'roles' in request.session:
        roles = request.session['roles']
        with connection.cursor() as cursor:
            if 'label' in roles:
                cursor.execute(f"SELECT nama, email FROM LABEL WHERE email = '{request.session['email']}'")
                row = cursor.fetchone()
                if row:
                    context['name'], context['email'], context['role'] = row[0], row[1], 'Label'
                    return render(request, 'dashboardlabel.html', context)
                
                
            elif len(roles) > 2:
                if 'artist' in roles and 'songwriter' in roles and 'podcaster' in roles:
                    role_ini = 'Artist, Songwriter, Podcaster'
                elif 'artist' in roles and 'songwriter' in roles:
                    role_ini = 'Artist, Songwriter'
                elif 'artist' in roles and 'podcaster' in roles:
                    role_ini = 'Artist, Podcaster'
                elif 'podcaster' in roles and 'songwriter' in roles:
                    role_ini = 'Podcaster, Songwriter'

                cursor.execute(f"SELECT nama, email, kota_asal, gender, tempat_lahir, tanggal_lahir FROM AKUN WHERE email = '{request.session['email']}'")
                row = cursor.fetchone()
                if row:
                    if row[3] == 0:
                        gender = "Laki-Laki"
                    else:
                        gender = "Perempuan"
                    context['name'], context['email'], context['kota_asal'], context['gender'], context['tempat_lahir'], context['tanggal_lahir'], context['role'] = row[0], row[1], row[2], gender, row[4], row[5], role_ini
                    return render(request, 'dashboardartist.html', context)
                
            elif 'podcaster' in roles:
                cursor.execute(f"SELECT nama, email, kota_asal, gender, tempat_lahir, tanggal_lahir FROM AKUN WHERE email = '{request.session['email']}'")
                row = cursor.fetchone()
                if row:
                    if row[3] == 0:
                        gender = "Laki-Laki"
                    else:
                        gender = "Perempuan"
                    context['name'], context['email'], context['kota_asal'], context['gender'], context['tempat_lahir'], context['tanggal_lahir'], context['role'] = row[0], row[1], row[2], gender, row[4], row[5], 'Podcaster'
                    return render(request, 'dashboardpodcaster.html', context)

            elif 'artist' in roles:
                cursor.execute(f"SELECT nama, email, kota_asal, gender, tempat_lahir, tanggal_lahir FROM AKUN WHERE email = '{request.session['email']}'")
                row = cursor.fetchone()
                if row:
                    if row[3] == 0:
                        gender = "Laki-Laki"
                    else:
                        gender = "Perempuan"
                    context['name'], context['email'], context['kota_asal'], context['gender'], context['tempat_lahir'], context['tanggal_lahir'], context['role'] = row[0], row[1], row[2], gender, row[4], row[5], 'Artist'
                    return render(request, 'dashboardartist.html', context)
                
            elif 'songwriter' in roles:
                cursor.execute(f"SELECT nama, email, kota_asal, gender, tempat_lahir, tanggal_lahir FROM AKUN WHERE email = '{request.session['email']}'")
                row = cursor.fetchone()
                if row:
                    if row[3] == 0:
                        gender = "Laki-Laki"
                    else:
                        gender = "Perempuan"
                    context['name'], context['email'], context['kota_asal'], context['gender'], context['tempat_lahir'], context['tanggal_lahir'], context['role'] = row[0], row[1], row[2], gender, row[4], row[5], 'Songwriter'
                    return render(request, 'dashboardartist.html', context)
                
            elif 'akun' in roles:
                cursor.execute(f"SELECT nama, email, kota_asal, gender, tempat_lahir, tanggal_lahir FROM AKUN WHERE email = '{request.session['email']}'")
                row = cursor.fetchone()
                if row:
                    if row[3] == 0:
                        gender = "Laki-Laki"
                    else:
                        gender = "Perempuan"
                    context['name'], context['email'], context['kota_asal'], context['gender'], context['tempat_lahir'], context['tanggal_lahir'], context['role'] = row[0], row[1], row[2], gender, row[4], row[5], 'Pengguna Biasa'
                    return render(request, 'dashboarduser.html', context)
    
    return HttpResponse("Role tidak ditemukan atau tidak valid.")

def show_royalties(request):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
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
