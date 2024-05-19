import uuid
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
import psycopg2
from django.contrib.auth.decorators import login_required
from albums.views import is_user_premium
from .models import Paket, Transaksi
from django.contrib import messages
from django.db import connection
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt


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
    
    email = request.session.get('email')
    is_premium = is_user_premium(email)
    
    context = {'is_premium' : is_premium}
    context['roles'] = request.session['roles']
    roles_splitted = []
    
    if 'roles' in request.session:
        roles = request.session['roles']
        with connection.cursor() as cursor:
            if 'label' in roles:
                cursor.execute(f"SELECT nama, email FROM LABEL WHERE email = '{request.session['email']}'")
                row = cursor.fetchone()
                if row:
                    context['name'], context['email'], context['role'] = row[0], row[1], 'Label'
                    return render(request, 'dashboardlabel.html', context)
            
            if ',' in roles: 
                roles_splitted = roles.split(",")

            if len(roles_splitted) > 2:
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
                    gender = "Laki-Laki" if row[3] == 0 else "Perempuan"
                    context['name'], context['email'], context['kota_asal'], context['gender'], context['tempat_lahir'], context['tanggal_lahir'], context['role'] = row[0], row[1], row[2], gender, row[4], row[5], role_ini
                    
                    # Menambahkan data tambahan sesuai role
                    if 'artist' in roles:
                        # Ambil lagu yang dinyanyikan
                        cursor.execute(f"SELECT K.judul FROM SONG S JOIN KONTEN K ON S.id_konten = K.id WHERE S.id_artist = (SELECT id FROM ARTIST WHERE email_akun = '{request.session['email']}')")
                        songs = cursor.fetchall()
                        context['songs'] = [song[0] for song in songs]
                    
                    if 'songwriter' in roles:
                        # Ambil lagu yang ditulis
                        cursor.execute(f"SELECT K.judul FROM SONGWRITER_WRITE_SONG SS JOIN SONG S ON SS.id_song = S.id_konten JOIN KONTEN K ON S.id_konten = K.id WHERE SS.id_songwriter = (SELECT id FROM SONGWRITER WHERE email_akun = '{request.session['email']}')")
                        written_songs = cursor.fetchall()
                        context['written_songs'] = [song[0] for song in written_songs]
                    
                    if 'podcaster' in roles:
                        # Ambil podcast yang dimiliki
                        cursor.execute(f"SELECT K.judul FROM PODCAST P JOIN KONTEN K ON P.id_konten = K.id WHERE P.email_podcaster = '{request.session['email']}'")
                        podcasts = cursor.fetchall()
                        context['podcasts'] = [podcast[0] for podcast in podcasts]

                    return render(request, 'dashboardartist.html', context)
                
            elif 'podcaster' in roles:
                cursor.execute(f"SELECT nama, email, kota_asal, gender, tempat_lahir, tanggal_lahir FROM AKUN WHERE email = '{request.session['email']}'")
                row = cursor.fetchone()
                if row:
                    gender = "Laki-Laki" if row[3] == 0 else "Perempuan"
                    context['name'], context['email'], context['kota_asal'], context['gender'], context['tempat_lahir'], context['tanggal_lahir'], context['role'] = row[0], row[1], row[2], gender, row[4], row[5], 'Podcaster'

                    # Menambahkan data tambahan sesuai role
                    cursor.execute(f"SELECT K.judul FROM PODCAST P JOIN KONTEN K ON P.id_konten = K.id WHERE P.email_podcaster = '{request.session['email']}'")
                    podcasts = cursor.fetchall()
                    context['podcasts'] = [podcast[0] for podcast in podcasts]

                    return render(request, 'dashboardpodcaster.html', context)

            elif 'artist' in roles:
                cursor.execute(f"SELECT nama, email, kota_asal, gender, tempat_lahir, tanggal_lahir FROM AKUN WHERE email = '{request.session['email']}'")
                row = cursor.fetchone()
                if row:
                    gender = "Laki-Laki" if row[3] == 0 else "Perempuan"
                    context['name'], context['email'], context['kota_asal'], context['gender'], context['tempat_lahir'], context['tanggal_lahir'], context['role'] = row[0], row[1], row[2], gender, row[4], row[5], 'Artist'
                    
                    # Menambahkan data tambahan sesuai role
                    cursor.execute(f"SELECT K.judul FROM SONG S JOIN KONTEN K ON S.id_konten = K.id WHERE S.id_artist = (SELECT id FROM ARTIST WHERE email_akun = '{request.session['email']}')")
                    songs = cursor.fetchall()
                    context['songs'] = [song[0] for song in songs]

                    return render(request, 'dashboardartist.html', context)
                
            elif 'songwriter' in roles:
                cursor.execute(f"SELECT nama, email, kota_asal, gender, tempat_lahir, tanggal_lahir FROM AKUN WHERE email = '{request.session['email']}'")
                row = cursor.fetchone()
                if row:
                    gender = "Laki-Laki" if row[3] == 0 else "Perempuan"
                    context['name'], context['email'], context['kota_asal'], context['gender'], context['tempat_lahir'], context['tanggal_lahir'], context['role'] = row[0], row[1], row[2], gender, row[4], row[5], 'Songwriter'

                    # Menambahkan data tambahan sesuai role
                    cursor.execute(f"SELECT K.judul FROM SONGWRITER_WRITE_SONG SS JOIN SONG S ON SS.id_song = S.id_konten JOIN KONTEN K ON S.id_konten = K.id WHERE SS.id_songwriter = (SELECT id FROM SONGWRITER WHERE email_akun = '{request.session['email']}')")
                    written_songs = cursor.fetchall()
                    context['written_songs'] = [song[0] for song in written_songs]

                    return render(request, 'dashboardartist.html', context)
                
            elif 'akun' in roles:
                cursor.execute(f"SELECT nama, email, kota_asal, gender, tempat_lahir, tanggal_lahir FROM AKUN WHERE email = '{request.session['email']}'")
                row = cursor.fetchone()
                if row:
                    gender = "Laki-Laki" if row[3] == 0 else "Perempuan"
                    context['name'], context['email'], context['kota_asal'], context['gender'], context['tempat_lahir'], context['tanggal_lahir'], context['role'] = row[0], row[1], row[2], gender, row[4], row[5], 'Pengguna Biasa'

                    # Menambahkan data tambahan sesuai role
                    cursor.execute(f"SELECT judul FROM USER_PLAYLIST WHERE email_pembuat = '{request.session['email']}'")
                    playlists = cursor.fetchall()
                    context['playlists'] = [playlist[0] for playlist in playlists]

                    return render(request, 'dashboarduser.html', context)
    
    return HttpResponse("Role tidak ditemukan atau tidak valid.")


def get_db_connection():
    # Get database credentials from environment variables
    db_name = 'postgres'
    db_user = 'postgres.ldbmqbscpwwvqiefvyhz'
    db_password = 'bashidup123'
    db_host = 'aws-0-ap-southeast-1.pooler.supabase.com'
    db_port = '5432'

    # Establish a connection to the database
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

    return conn
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
        'roles':request.session['roles']
    }

    return render(request, 'cek_royalti.html', context)


def daftar_paket(request):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    context = {
        'pakets': []
    }
    query = """
    SELECT * FROM PAKET
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO public')
            cursor.execute(query)
            pakets = cursor.fetchall()
            for paket in pakets:
                p = {
                    'jenis': paket[0],
                    'harga': format_rupiah(paket[1]),
                }
                context['pakets'].append(p)
            context['roles'] = request.session['roles']
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
    return render(request, 'daftar_paket.html', context)

@csrf_exempt
def berlangganan_paket(request, jenis_paket):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    if request.method == 'POST':
        id = uuid.uuid4()
        jenis_paket = request.POST.get('jenis')
        email = request.session['email'] 
        timestamp_dimulai = datetime.now()
        timestamp_berakhir = update_timestamp(timestamp_dimulai, jenis_paket)
        metode_bayar = request.POST.get('metode_bayar')
        nominal = reverse_format_rupiah(request.POST.get('nominal'))

        try:
            with connection.cursor() as cursor:
                cursor.execute('SET search_path TO public')
                
                cursor.execute(f"""
                INSERT INTO TRANSACTION (id, jenis_paket, email, timestamp_dimulai, timestamp_berakhir, metode_bayar, nominal)
                VALUES ('{id}', '{jenis_paket}', '{email}', '{timestamp_dimulai}', '{timestamp_berakhir}', '{metode_bayar}', {nominal})
                """)
                connection.commit()
                
                cursor.execute(f"""
                INSERT INTO PREMIUM (email)
                VALUES ('{email}')
                """)
                connection.commit()
        except Exception as e:
            messages.error(request, str(e).splitlines()[0])
            return redirect('main:daftar_paket')
        messages.success(request, 'Berhasil berlangganan paket!')
        return redirect('main:daftar_paket')
    
    query = f"""
    SELECT * FROM PAKET WHERE jenis = '{jenis_paket}'
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO public')
            cursor.execute(query)
            paket = cursor.fetchone()
            context = {
                'jenis': paket[0],
                'harga': format_rupiah(paket[1]),
                'roles':request.session['roles']
            }
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('daftar_paket')
    return render(request, 'berlangganan_paket.html', context)

@csrf_exempt
def search(request):
    if not has_logged_in(request):
        return redirect('authentication:show_start')

    if request.method == 'POST':
        search_text = request.POST.get('search')

        query_playlist = f"""
        SELECT 
            UP.id_playlist,
            UP.judul, 
            A.nama
        FROM 
            USER_PLAYLIST UP
        JOIN 
            AKUN A ON UP.email_pembuat = A.email
        WHERE 
            UP.judul ILIKE '%{search_text}%'
        """

        query_song = f"""
        SELECT s.id_konten, k.judul, a.nama
        FROM SONG s
        JOIN ARTIST ar ON s.id_artist = ar.id
        JOIN AKUN a ON ar.email_akun = a.email
        JOIN KONTEN k ON s.id_konten = k.id
        WHERE k.judul ILIKE '%{search_text}%'
        """

        query_podcast = f"""
        SELECT pc.id_konten, k.judul, a.nama
        FROM PODCAST pc
        JOIN PODCASTER p ON pc.email_podcaster = p.email
        JOIN AKUN a ON p.email = a.email
        JOIN KONTEN k ON pc.id_konten = k.id
        WHERE k.judul ILIKE '%{search_text}%'
        """

        context = {
            'search_text': search_text,
            'playlists': [],
            'songs': [],
            'podcasts': [],
        }

        try:
            with connection.cursor() as cursor:
                cursor.execute('SET search_path TO public')
                
                cursor.execute(query_playlist)
                playlists = cursor.fetchall()
                for playlist in playlists:
                    p = {
                        'id': playlist[0],
                        'judul': playlist[1],
                        'oleh': playlist[2],
                        'tipe': 'USER PLAYLIST'
                    }
                    context['playlists'].append(p)
                
                cursor.execute(query_song)
                songs = cursor.fetchall()
                for song in songs:
                    s = {
                        'id': song[0],
                        'judul': song[1],
                        'oleh': song[2],
                        'tipe': 'SONG'
                    }
                    context['songs'].append(s)
                
                cursor.execute(query_podcast)
                podcasts = cursor.fetchall()
                for podcast in podcasts:
                    p = {
                        'id': podcast[0],
                        'judul': podcast[1],
                        'oleh': podcast[2],
                        'tipe': 'PODCAST'
                    }
                    context['podcasts'].append(p)
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')

        return render(request, 'search.html', context)
    return render(request, 'dashboardlabel.html')


def riwayat_transaksi(request):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO public')
            cursor.execute(f"""
            SELECT * FROM TRANSACTION WHERE email = '{request.session['email']}'
            """)
            transactions = cursor.fetchall()
            context = {
                'transactions': [],
                'roles':request.session['roles']
            }
            for transaction in transactions:
                t = {
                    'id': transaction[0],
                    'jenis_paket': transaction[1],
                    'email': transaction[2],
                    'tanggal_dimulai': transaction[3],
                    'tanggal_berakhir': transaction[4],
                    'metode_pembayaran': transaction[5],
                    'nominal': format_rupiah(transaction[6]),
                }
                context['transactions'].append(t)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('main:show_dashboard')
    return render(request, 'riwayat_transaksi.html', context)

def show_homepage(request):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    email = request.session.get('email')
    is_premium = is_user_premium(email)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    
    query_songs = """
        SELECT K.id, K.judul, A.nama
        FROM SONG S
        JOIN KONTEN K ON S.id_konten = K.id
        JOIN ARTIST AR ON S.id_artist = AR.id
        JOIN AKUN A ON AR.email_akun = A.email;
    """
    cursor.execute(query_songs)
    songs = cursor.fetchall()

    query_podcasts = """
        SELECT P.id_konten, K.judul, A.nama
        FROM PODCAST P
        JOIN KONTEN K ON P.id_konten = K.id
        JOIN PODCASTER PR ON P.email_podcaster = PR.email
        JOIN AKUN A ON PR.email = A.email;
    """
    cursor.execute(query_podcasts)
    podcasts = cursor.fetchall()

    query_playlists = """
        SELECT UP.id_user_playlist, UP.judul, A.nama
        FROM USER_PLAYLIST UP
        JOIN AKUN A ON UP.email_pembuat = A.email;
    """
    cursor.execute(query_playlists)
    playlists = cursor.fetchall()

    cursor.close()
    conn.close()

    return render(request, 'homepage.html', {
        'songs': songs,
        'podcasts': podcasts,
        'playlists': playlists,
        'roles':request.session['roles'],
        'is_premium' : is_premium
    })

def format_rupiah(amount):
    # Convert the amount to an integer (if it's not already)
    amount = int(amount)
    
    # Format the number with commas as thousand separators
    formatted_amount = f"{amount:,.0f}"
    
    # Replace commas with dots
    formatted_amount = formatted_amount.replace(",", ".")
    
    # Add the "Rp" prefix
    return f"Rp{formatted_amount}"

def reverse_format_rupiah(formatted_amount):
    # Convert the formatted amount to a string (if it's not already)
    formatted_amount = str(formatted_amount)

    # Remove the "Rp" prefix
    if formatted_amount.startswith("Rp"):
        formatted_amount = formatted_amount[2:]
    
    # Replace dots with commas (if necessary)
    formatted_amount = formatted_amount.replace(".", "")
    
    # Convert the cleaned string to an integer
    amount = int(formatted_amount)
    
    return amount

def update_timestamp(timestamp, jenis):    
    if jenis == "1 bulan":
        timestamp += timedelta(days=30)
    elif jenis == "3 bulan":
        timestamp += timedelta(days=90)
    elif jenis == "6 bulan":
        timestamp += timedelta(days=180)
    elif jenis == "1 tahun":
        timestamp += timedelta(days=365)
    
    return timestamp