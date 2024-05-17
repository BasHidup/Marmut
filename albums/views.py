from datetime import datetime
from uuid import uuid4
import uuid
from django.conf import settings
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
import psycopg2
from django.http import HttpResponse, HttpResponseServerError
from django.template import loader
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from albums.models import DownloadedSong


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
def has_logged_in(request):
    print(request.session['email'])
    print(request.session['roles'])
    if request.session['email'] == 'not found' or request.session['roles'] == 'not found':
        return False
    
    return True

def show_albums(request):
    if not has_logged_in(request):
        return redirect('authentication:show_start')

    label_acc = None
    label_id = None
    albums = []
    cursor = connection.cursor()
    if 'roles' in request.session and 'label' in request.session['roles']:
        try:
            cursor.execute('SET search_path TO public')
            email = request.session['email']
            query_label_name = f"SELECT nama, id FROM LABEL WHERE email = '{email}'"
            cursor.execute(query_label_name)
            label_name_result = cursor.fetchone()
            if label_name_result:
                label_acc = label_name_result[0]
                label_id = label_name_result[1]

        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')

    # Menambahkan data album ke dalam list albums
    cursor.execute("""
        SELECT a.id, a.judul, a.jumlah_lagu, a.id_label, a.total_durasi, l.nama AS label_name
        FROM ALBUM a
        INNER JOIN LABEL l ON a.id_label = l.id
    """)
    album_results = cursor.fetchall()
    for album_result in album_results:
        album = {
            'id': album_result[0],
            'judul': album_result[1],
            'jumlah_lagu': album_result[2],
            'label': album_result[5],
            'total_durasi': album_result[4]
        }
        albums.append(album)
    
    if (label_acc):
        albums = [album for album in albums if album['label'] == label_acc]

    context = {
        'albums':albums,
        'label_acc':label_acc,
    }

    return render(request, "list_albums.html", context)

def create_album(request):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    cursor = connection.cursor()
    cursor.execute('SET search_path TO public')

    if request.method == 'POST':
        judul = request.POST.get('judul_album')
        id_label = request.POST.get('id_label')


        # Validasi data, misalnya pastikan judul tidak kosong
        if not judul:
            return render(request, 'create_album.html', {'error': 'Judul tidak boleh kosong'})
        
        # Generate UUID untuk id album baru
        id_album = uuid4()

        # Query untuk insert data album baru ke tabel ALBUM
        query = f"INSERT INTO ALBUM (id, judul, jumlah_lagu, id_label, total_durasi) VALUES ('{id_album}', '{judul}', 0, '{id_label}', 0);"
        cursor.execute(query)

        id_album_ini = id_album
        judul_lagu = request.POST.get('judul')
        artist_id = request.POST.get('artist')
        songwriters_ids = request.POST.getlist('songwriter')
        genres = request.POST.getlist('genre')
        durasi = request.POST.get('durasi')
        tanggal_rilis = datetime.now().date()
        tahun = datetime.now().year

        # Validasi data, misalnya pastikan judul tidak kosong
        if not judul_lagu or not artist_id or not songwriters_ids or not genres:
            return render(request, 'create_album.html', {'error': 'Semua field tidak boleh kosong'})
        
        id_konten = uuid4()

        # Query untuk insert data album baru ke tabel ALBUM
        query_konten = f"""
            INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi) 
            VALUES ('{id_konten}', '{judul_lagu}', '{tanggal_rilis}', '{tahun}', {durasi});
        """
        cursor.execute(query_konten)

        # Query insert ke song
        query_song = f"""
            INSERT INTO SONG (id_konten, id_artist, id_album, total_play, total_download) 
            VALUES ('{id_konten}', '{artist_id}', '{id_album_ini}', 0, 0)
        """
        cursor.execute(query_song)

        # Query insert songwriter write song
        query_sw_w_s = """
            INSERT INTO SONGWRITER_WRITE_SONG (id_songwriter, id_song) 
            VALUES (%s, %s)
        """
        for songwriter_id in songwriters_ids:
            cursor.execute(query_sw_w_s, [songwriter_id, id_konten])

        # query genre
        for genre in genres:
            query_genre = """
                INSERT INTO GENRE (id_konten, genre)
                VALUES (%s, %s)
            """
            cursor.execute(query_genre, [id_konten, genre])
        
        # Insert into ROYALTI table
        processed_pemilik_hak_cipta = set()

        # Get id_pemilik_hak_cipta for the artist
        cursor.execute("SELECT id_pemilik_hak_cipta FROM ARTIST WHERE id = %s", [artist_id])
        artist_pemilik_hak_cipta = cursor.fetchone()[0]
        print("disini line 415", artist_pemilik_hak_cipta)
        if artist_pemilik_hak_cipta not in processed_pemilik_hak_cipta:
            query_royalti = """
                INSERT INTO ROYALTI (id_pemilik_hak_cipta, id_song, jumlah)
                VALUES (%s, %s, 0)
            """
            cursor.execute(query_royalti, [artist_pemilik_hak_cipta, id_konten])
            processed_pemilik_hak_cipta.add(artist_pemilik_hak_cipta)

        # Get id_pemilik_hak_cipta for each songwriter
        for songwriter_id in songwriters_ids:
            cursor.execute("SELECT id_pemilik_hak_cipta FROM SONGWRITER WHERE id = %s", [songwriter_id])
            songwriter_pemilik_hak_cipta = cursor.fetchone()[0]
            print("disini line 428", songwriter_pemilik_hak_cipta)
            if songwriter_pemilik_hak_cipta not in processed_pemilik_hak_cipta:
                cursor.execute(query_royalti, [songwriter_pemilik_hak_cipta, id_konten])
                processed_pemilik_hak_cipta.add(songwriter_pemilik_hak_cipta)


        return redirect('albums:show_albums') 

    labels = []
    cursor = connection.cursor()
    cursor.execute('SET search_path TO public')

    cursor.execute("""
        SELECT l.nama, l.id
        FROM LABEL l
    """)
    label_results = cursor.fetchall()
    for label_result in label_results:
        label = {
            'nama': label_result[0],
            'id':label_result[1]
        }
        labels.append(label)

    akun_ar = None
    akun_sw = None

    if 'roles' in request.session:
        if 'artist' in request.session['roles']:
            query_artist_acc = f"""
                SELECT u.nama, ar.id
                FROM AKUN u JOIN ARTIST ar ON u.email = ar.email_akun
                WHERE u.email = '{request.session['email']}'
            """
            cursor.execute(query_artist_acc)
            artist_result = cursor.fetchone()
            akun_ar = {'name': artist_result[0], 'id': artist_result[1]}

        if 'songwriter' in request.session['roles']:
            query_sw_acc = f"""
                SELECT u.nama, sw.id
                FROM AKUN u JOIN SONGWRITER sw ON u.email = sw.email_akun
                WHERE u.email = '{request.session['email']}'
            """
            cursor.execute(query_sw_acc)
            sw_result = cursor.fetchone()
            akun_sw = {'name': sw_result[0], 'id': sw_result[1]}

    query_artist = f"""
        SELECT u.nama, ar.id
        FROM AKUN u JOIN ARTIST ar ON u.email = ar.email_akun
    """
    cursor.execute(query_artist)
    artists_result = cursor.fetchall()
    artists = [
        {
            'name': artist[0], 
            'id': artist[1], 
        } for artist in artists_result
    ]

    query_sw = f"""
        SELECT u.nama, sw.id
        FROM AKUN u JOIN SONGWRITER sw ON u.email = sw.email_akun
    """
    cursor.execute(query_sw)
    sw_result = cursor.fetchall()
    songwriter = [
        {
            'name': sw[0], 
            'id': sw[1], 
        } for sw in sw_result
    ]

    query_genres = "SELECT DISTINCT genre FROM GENRE"
    cursor.execute(query_genres)
    genres_result = cursor.fetchall()
    genres = [{'jenis': genre[0]} for genre in genres_result]

    context = {
        'akun_ar':akun_ar,
        'akun_sw':akun_sw,
        'artists':artists,
        'songwriters':songwriter,
        'genres':genres,
        'labels':labels,
    }

    return render(request, "create_album.html", context)

def delete_album(request, id_album):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    try:
        with connection.cursor() as cursor:
            # Get all song ids associated with the album
            get_song_ids_query = """
                SELECT id_konten FROM SONG WHERE id_album = %s
            """
            cursor.execute(get_song_ids_query, [id_album])
            song_ids = cursor.fetchall()
            
            for id_song in song_ids:
                # Delete from ROYALTI
                delete_royalty = """
                    DELETE FROM ROYALTI WHERE id_song = %s
                """
                cursor.execute(delete_royalty, [id_song])

                # Delete from SONGWRITER_WRITE_SONG
                delete_songwriter_write_song = """
                    DELETE FROM SONGWRITER_WRITE_SONG WHERE id_song = %s
                """
                cursor.execute(delete_songwriter_write_song, [id_song])
                
                # Delete from GENRE
                delete_genre = """
                    DELETE FROM GENRE WHERE id_konten = %s
                """
                cursor.execute(delete_genre, [id_song])
                
                # Delete from SONG
                delete_song = """
                    DELETE FROM SONG WHERE id_konten = %s
                """
                cursor.execute(delete_song, [id_song])
                
                # Delete from KONTEN
                delete_konten = """
                    DELETE FROM KONTEN WHERE id = %s
                """
                cursor.execute(delete_konten, [id_song])
            
            # Finally, delete the album
            delete_album_query = """
                DELETE FROM ALBUM WHERE id = %s
            """
            cursor.execute(delete_album_query, [id_album])
    
    except Exception as e:
        # Handle exceptions, log the error, etc.
        print(f"An error occurred: {e}")

    return redirect('albums:show_albums')

def show_songs(request, id_album):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    id_album_ini = id_album
    label_acc = None
    songs = []
    cursor = connection.cursor()

    if 'roles' in request.session and 'label' in request.session['roles']:
        try:
            cursor.execute('SET search_path TO public')
            email = request.session['email']
            query_label_name = f"SELECT nama, id FROM LABEL WHERE email = '{email}'"
            cursor.execute(query_label_name)
            label_name_result = cursor.fetchone()
            if label_name_result:
                label_acc = label_name_result[0]
                label_id = label_name_result[1]

        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    # Query to get album details
    query_album = "SELECT judul FROM album WHERE id = %s"
    cursor.execute(query_album, [id_album_ini])
    album_name_result = cursor.fetchone()
    album_name = album_name_result[0] if album_name_result else None

    # Query to get songs in the album
    query_songs = """
    SELECT 
        s.id_konten, s.id_artist, s.id_album, s.total_play, s.total_download, 
        k.judul AS judul_album, k.durasi
    FROM 
        song s
        JOIN konten k ON s.id_konten = k.id
    WHERE 
        s.id_album = %s
    """
    # print(id_album_ini)
    cursor.execute(query_songs, [id_album_ini])
    songs_result = cursor.fetchall()

    if not songs_result:
        print(f"No songs found for album id {id_album_ini}")
    else:
        print(f"Found songs: {songs_result}")

    songs = [
        {
            'id_konten': song[0], 
            'id_artist': song[1], 
            'id_album': song[2], 
            'total_play': song[3], 
            'total_download': song[4], 
            'judul': song[5], 
            'durasi': song[6]
        } for song in songs_result
    ]

    print('----------------------------------------')
    # print(songs)

    context = {
        'album_name':album_name,
        'id_album':id_album_ini,
        'songs':songs,
        'label_acc':label_acc,
    }

    return render(request, "list_songs.html", context)

def create_song(request, id_album):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    cursor = connection.cursor()
    cursor.execute('SET search_path TO public')

    if request.method == 'POST':
        id_album_ini = id_album
        judul_lagu = request.POST.get('judul')
        artist_id = request.POST.get('artist')
        songwriters_ids = request.POST.getlist('songwriter')
        genres = request.POST.getlist('genre')
        durasi = request.POST.get('durasi')
        tanggal_rilis = datetime.now().date()
        tahun = datetime.now().year

        # Validasi data, misalnya pastikan judul tidak kosong
        if not judul_lagu or not artist_id or not songwriters_ids or not genres:
            return render(request, 'create_album.html', {'error': 'Semua field tidak boleh kosong'})
        
        id_konten = uuid4()

        # Query untuk insert data album baru ke tabel ALBUM
        query_konten = f"""
            INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi) 
            VALUES ('{id_konten}', '{judul_lagu}', '{tanggal_rilis}', '{tahun}', {durasi});
        """
        cursor.execute(query_konten)

        # Query insert ke song
        query_song = f"""
            INSERT INTO SONG (id_konten, id_artist, id_album, total_play, total_download) 
            VALUES ('{id_konten}', '{artist_id}', '{id_album_ini}', 0, 0)
        """
        cursor.execute(query_song)

        # Query insert songwriter write song
        query_sw_w_s = """
            INSERT INTO SONGWRITER_WRITE_SONG (id_songwriter, id_song) 
            VALUES (%s, %s)
        """
        for songwriter_id in songwriters_ids:
            cursor.execute(query_sw_w_s, [songwriter_id, id_konten])

        # query genre
        for genre in genres:
            query_genre = """
                INSERT INTO GENRE (id_konten, genre)
                VALUES (%s, %s)
            """
            cursor.execute(query_genre, [id_konten, genre])

        # Insert into ROYALTI table
        processed_pemilik_hak_cipta = set()

        # Get id_pemilik_hak_cipta for the artist
        cursor.execute("SELECT id_pemilik_hak_cipta FROM ARTIST WHERE id = %s", [artist_id])
        artist_pemilik_hak_cipta = cursor.fetchone()[0]
        print("disini line 415", artist_pemilik_hak_cipta)
        if artist_pemilik_hak_cipta not in processed_pemilik_hak_cipta:
            query_royalti = """
                INSERT INTO ROYALTI (id_pemilik_hak_cipta, id_song, jumlah)
                VALUES (%s, %s, 0)
            """
            cursor.execute(query_royalti, [artist_pemilik_hak_cipta, id_konten])
            processed_pemilik_hak_cipta.add(artist_pemilik_hak_cipta)

        # Get id_pemilik_hak_cipta for each songwriter
        for songwriter_id in songwriters_ids:
            cursor.execute("SELECT id_pemilik_hak_cipta FROM SONGWRITER WHERE id = %s", [songwriter_id])
            songwriter_pemilik_hak_cipta = cursor.fetchone()[0]
            print("disini line 428", songwriter_pemilik_hak_cipta)
            if songwriter_pemilik_hak_cipta not in processed_pemilik_hak_cipta:
                cursor.execute(query_royalti, [songwriter_pemilik_hak_cipta, id_konten])
                processed_pemilik_hak_cipta.add(songwriter_pemilik_hak_cipta)

        return redirect('albums:show_songs', id_album=id_album) 

    id_album_ini = id_album
    akun_ar = None
    akun_sw = None

    if 'roles' in request.session:
        if 'artist' in request.session['roles']:
            query_artist_acc = f"""
                SELECT u.nama, ar.id
                FROM AKUN u JOIN ARTIST ar ON u.email = ar.email_akun
                WHERE u.email = '{request.session['email']}'
            """
            cursor.execute(query_artist_acc)
            artist_result = cursor.fetchone()
            akun_ar = {'name': artist_result[0], 'id': artist_result[1]}

        if 'songwriter' in request.session['roles']:
            query_sw_acc = f"""
                SELECT u.nama, sw.id
                FROM AKUN u JOIN SONGWRITER sw ON u.email = sw.email_akun
                WHERE u.email = '{request.session['email']}'
            """
            cursor.execute(query_sw_acc)
            sw_result = cursor.fetchone()
            akun_sw = {'name': sw_result[0], 'id': sw_result[1]}

    query_album = "SELECT judul FROM album WHERE id = %s"
    cursor.execute(query_album, [id_album_ini])
    album_name_result = cursor.fetchone()
    album_name = album_name_result[0] if album_name_result else None

    query_artist = f"""
        SELECT u.nama, ar.id
        FROM AKUN u JOIN ARTIST ar ON u.email = ar.email_akun
    """
    cursor.execute(query_artist)
    artists_result = cursor.fetchall()
    artists = [
        {
            'name': artist[0], 
            'id': artist[1], 
        } for artist in artists_result
    ]

    query_sw = f"""
        SELECT u.nama, sw.id
        FROM AKUN u JOIN SONGWRITER sw ON u.email = sw.email_akun
    """
    cursor.execute(query_sw)
    sw_result = cursor.fetchall()
    songwriter = [
        {
            'name': sw[0], 
            'id': sw[1], 
        } for sw in sw_result
    ]

    query_genres = "SELECT DISTINCT genre FROM GENRE"
    cursor.execute(query_genres)
    genres_result = cursor.fetchall()
    genres = [{'jenis': genre[0]} for genre in genres_result]

    context = {
        'akun_ar':akun_ar,
        'akun_sw':akun_sw,
        'id_album':id_album,
        'album_name':album_name,
        'artists':artists,
        'songwriters':songwriter,
        'genres':genres,
    }

    return render(request, 'create_song.html', context)


def show_song_detail(request, id_song):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    cursor = connection.cursor()
    cursor.execute('SET search_path TO public')
    query_song = """
            SELECT 
                k.judul AS song_title, 
                u.nama AS artist_name, 
                k.tanggal_rilis, 
                k.tahun, 
                k.durasi, 
                s.total_play, 
                s.total_download, 
                a.judul AS album_title,
                a.id
            FROM 
                KONTEN k
            JOIN 
                SONG s ON k.id = s.id_konten
            JOIN 
                ALBUM a ON a.id = s.id_album
            JOIN 
                ARTIST ar ON ar.id = s.id_artist
            JOIN 
                AKUN u ON u.email = ar.email_akun
            WHERE 
                k.id = %s
        """
    cursor.execute(query_song, [id_song])
    song_result = cursor.fetchone()

    song = {
        'id_konten': id_song,
        'judul': song_result[0],
        'artist': song_result[1],
        'tanggal_rilis': song_result[2],
        'tahun': song_result[3],
        'durasi': song_result[4],
        'total_play': song_result[5],
        'total_download': song_result[6],
        'judul_album': song_result[7],
        'id_album': song_result[8]
    }
    # print(song)
    
    label_acc = None
    context = {
        'song':song,
        'label_acc':label_acc,
    }

    return render(request, 'song_detail.html', context)

def delete_song(request, id_album, id_song):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    with connection.cursor() as cursor:
        # Delete from ROYALTI
        delete_royalty = """
            DELETE FROM ROYALTI WHERE id_song = %s
        """
        cursor.execute(delete_royalty, [id_song])

        # Delete from SONGWRITER_WRITE_SONG
        delete_songwriter_write_song = """
            DELETE FROM SONGWRITER_WRITE_SONG WHERE id_song = %s
        """
        cursor.execute(delete_songwriter_write_song, [id_song])
        
        # Delete from GENRE
        delete_genre = """
            DELETE FROM GENRE WHERE id_konten = %s
        """
        cursor.execute(delete_genre, [id_song])
        
        # Delete from SONG
        delete_song = """
            DELETE FROM SONG WHERE id_konten = %s
        """
        cursor.execute(delete_song, [id_song])
        
        # Finally, delete from KONTEN
        delete_konten = """
            DELETE FROM KONTEN WHERE id = %s
        """
        cursor.execute(delete_konten, [id_song])

    return redirect('albums:show_songs', id_album=id_album) 

def downloaded_songs(request):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    context = {
        'downloaded_songs': []
    }
    email_downloader = request.session['email']

    query = f"""
    SELECT 
        ds.id_song,
        k.judul AS judul_lagu,
        a.nama AS nama_artist
    FROM 
        DOWNLOADED_SONG ds
    JOIN 
        SONG s ON ds.id_song = s.id_konten
    JOIN 
        KONTEN k ON s.id_konten = k.id
    JOIN 
        ARTIST ar ON s.id_artist = ar.id
    JOIN 
        AKUN a ON ar.email_akun = a.email
    WHERE 
        ds.email_downloader = '{email_downloader}';
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO public')
            
            cursor.execute(query)
            downloaded_songs = cursor.fetchall()
            
            for song in downloaded_songs:
                context['downloaded_songs'].append({
                    'id': song[0],
                    'title': song[1],
                    'artist': song[2]
                })
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
    return render(request, 'downloaded_songs.html', context)

def delete_downloaded_song(request, downloaded_song_id):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
    if request.method == 'POST':
        email_downloader = request.session['email']
        query = f"""
        DELETE FROM DOWNLOADED_SONG
        WHERE id_song = '{downloaded_song_id}' AND email_downloader = '{email_downloader}';
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute('SET search_path TO public')
                cursor.execute(query)
                connection.commit()
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('albums:downloaded_songs')



@csrf_exempt
def manage_playlists(request):
    # Memeriksa apakah pengguna telah masuk atau belum
    if 'email' in request.session:
        # Mengambil email pengguna dari sesi
        email = request.session.get('email')

        try:
            with connection.cursor() as cursor:
                cursor.execute('SET search_path TO public')
                # Query untuk mendapatkan playlist pengguna berdasarkan email
                query = """
                SELECT UP.id_playlist AS id_playlist,
                UP.judul AS judul_playlist, 
                UP.jumlah_lagu AS jumlah_lagu,
                UP.total_durasi AS total_durasi
                FROM USER_PLAYLIST UP
                JOIN AKUN A ON UP.email_pembuat = A.email
                WHERE A.email = %s;
                """
                cursor.execute(query, (email,))
                rows = cursor.fetchall()
                playlists = [{'id': row[0],'judul': row[1], 'jumlah_lagu': row[2], 'total_durasi': row[3]} for row in rows]

        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            playlists = []

        return render(request, 'manageplaylist.html', {'playlists': playlists})
    else:
        # Jika pengguna belum masuk, arahkan ke halaman login
        return redirect('authentication:login_view')

def add_playlist(request):
    if request.method == 'POST':
        judul = request.POST['judul']
        deskripsi = request.POST['deskripsi']
        id_playlist = uuid.uuid4()
        id_user_playlist = uuid.uuid4()
        
        # Menambahkan id_playlist ke tabel PLAYLIST
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO PLAYLIST (id) VALUES (%s)", (id_playlist,))
        conn.commit()
        
        tanggal_dibuat = datetime.now().date()
        email_pembuat = request.session.get('email')
        cursor.execute("""
            INSERT INTO USER_PLAYLIST (email_pembuat, id_user_playlist, judul, deskripsi, jumlah_lagu, tanggal_dibuat, id_playlist, total_durasi)
            VALUES (%s, %s, %s, %s, 0, %s, %s, 0)
        """, (email_pembuat, id_user_playlist, judul, deskripsi, tanggal_dibuat, id_playlist))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('albums:manage_playlists')
    return render(request, 'addplaylist.html')

def playlist_detail(request, playlist_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    queryplaylist = """
                SELECT id_playlist, judul, email_pembuat, jumlah_lagu, total_durasi, tanggal_dibuat, deskripsi, id_user_playlist FROM USER_PLAYLIST WHERE id_playlist = %s;
                """
    cursor.execute(queryplaylist, (playlist_id,))
    playlistrow = cursor.fetchone()
    playlist = {
        'id' : playlistrow[0],
        'judul': playlistrow[1],
        'email_pembuat': playlistrow[2],
        'jumlah_lagu': playlistrow[3],
        'total_durasi': playlistrow[4],
        'tanggal_dibuat': playlistrow[5],
        'deskripsi': playlistrow[6]
    }
    
    if playlist:
        querysongs = """
        SELECT
        SONG.id_konten AS id_lagu,
        KONTEN.judul AS judul_lagu,
        KONTEN.durasi AS durasi_lagu,
        AKUN.nama AS nama_artis
        FROM
            USER_PLAYLIST
        JOIN
            PLAYLIST_SONG ON USER_PLAYLIST.id_playlist = PLAYLIST_SONG.id_playlist
        JOIN
            SONG ON PLAYLIST_SONG.id_song = SONG.id_konten
        JOIN
            KONTEN ON SONG.id_konten = KONTEN.id
        JOIN
            ARTIST ON SONG.id_artist = ARTIST.id
        JOIN
            AKUN ON ARTIST.email_akun = AKUN.email
        WHERE
            USER_PLAYLIST.id_playlist = %s;
                """
        cursor.execute(querysongs, (playlist_id,))
        songsrow = cursor.fetchall()
        songs = [{'id_lagu': row[0],'judul_lagu': row[1], 'durasi_lagu': row[2], 'nama_penyanyi': row[3]} for row in songsrow]
    else:
        songs = []
    cursor.close()
    conn.close()
    return render(request, 'playlistdetail.html', {'playlist': playlist, 'songs': songs})


def edit_playlist(request, playlist_id):
    if request.method == 'POST':
        judul = request.POST['judul']
        deskripsi = request.POST['deskripsi']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE USER_PLAYLIST SET judul = %s, deskripsi = %s WHERE id_user_playlist = %s", (judul, deskripsi, playlist_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('albums:manage_playlists')  
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT judul, deskripsi FROM USER_PLAYLIST WHERE id_user_playlist = %s", (playlist_id,))
    playlist = cursor.fetchone()
    cursor.close()
    conn.close()
    return render(request, 'editplaylist.html', {'playlist': playlist})

def delete_playlist(request, playlist_id):
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Mengambil id_user_playlist dari id_playlist
        cursor.execute("SELECT id_user_playlist FROM USER_PLAYLIST WHERE id_playlist = %s", (playlist_id,))
        id_user_playlist = cursor.fetchone()[0]

        
        cursor.execute("DELETE FROM AKUN_PLAY_USER_PLAYLIST WHERE id_user_playlist = %s", (id_user_playlist,))

        cursor.execute("DELETE FROM USER_PLAYLIST WHERE id_playlist = %s", (playlist_id,))
        
        cursor.execute("DELETE FROM PLAYLIST_SONG WHERE id_playlist = %s", (playlist_id,))

        cursor.execute("DELETE FROM PLAYLIST WHERE id = %s", (playlist_id,))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect('albums:manage_playlists')


def add_song_to_playlist(request, playlist_id):
    if request.method == 'POST':
        song_id = request.POST['song_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM PLAYLIST_SONG WHERE id_playlist = %s AND id_song = %s", (playlist_id, song_id))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO PLAYLIST_SONG (id_playlist, id_song) VALUES (%s, %s)", (playlist_id, song_id))
            conn.commit()
            messages.success(request, 'Lagu berhasil ditambahkan ke playlist.')
        else:
            messages.error(request, 'Lagu sudah ada di playlist.')
        cursor.close()
        conn.close()
        return redirect('albums:playlist_detail', playlist_id=playlist_id)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT S.id_konten, K.judul, AKUN.nama AS nama_artis FROM SONG S JOIN KONTEN K ON S.id_konten = K.id JOIN ARTIST A ON S.id_artist = A.id JOIN AKUN ON A.email_akun = AKUN.email;")
    songsrow = cursor.fetchall()
    songs = [{'id_lagu': row[0], 'judul_lagu': row[1], 'nama_penyanyi': row[2]} for row in songsrow]
    cursor.close()
    conn.close()
    return render(request, 'addsongtoplaylist.html', {'songs': songs})

def play_song(request, song_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    email = request.session.get('email')
    is_premium = is_user_premium(email)

    if request.method == 'POST':
        progress = int(request.POST.get('progress', 0))
        if progress > 70:
            timestamp = datetime.now()
            cursor.execute("INSERT INTO AKUN_PLAY_SONG (email_pemain, id_song, waktu) VALUES (%s, %s, %s)", (email, song_id, timestamp))
            conn.commit()
            cursor.execute("UPDATE SONG SET total_play = total_play + 1 WHERE id_konten = %s", (song_id,))
            conn.commit()
            messages.success(request, 'Lagu berhasil dimainkan.')
        else:
            messages.error(request, 'Progress harus lebih dari 70% untuk memainkan lagu.')

    querysongs = """
    SELECT 
    K.id AS "id_lagu",
    K.judul AS "judul_lagu",
    ARRAY_AGG(DISTINCT G.genre) AS "genre_lagu",
    A1.nama AS "nama_penyanyi",
    ARRAY_AGG(DISTINCT A2.nama) AS "penulis_lagu",
    K.durasi AS "durasi_lagu",
    K.tanggal_rilis AS "tanggal_rilis_lagu",
    K.tahun AS "tahun_rilis_lagu",
    S.total_play AS "total_dimainkan",
    S.total_download AS "total_download",
    COALESCE(AL.judul, 'Unknown') AS "judul_album"
    FROM 
        SONG S
    JOIN 
        KONTEN K ON S.id_konten = K.id
    LEFT JOIN 
        ALBUM AL ON S.id_album = AL.id
    JOIN 
        ARTIST AR ON S.id_artist = AR.id
    JOIN 
        AKUN A1 ON AR.email_akun = A1.email
    LEFT JOIN 
        SONGWRITER_WRITE_SONG SWS ON S.id_konten = SWS.id_song
    LEFT JOIN 
        SONGWRITER SW ON SWS.id_songwriter = SW.id
    LEFT JOIN 
        AKUN A2 ON SW.email_akun = A2.email
    LEFT JOIN 
        GENRE G ON K.id = G.id_konten
    WHERE 
        K.id = %s
    GROUP BY 
        K.id, K.judul, A1.nama, K.durasi, K.tanggal_rilis, K.tahun, S.total_play, S.total_download, AL.judul;
    """
    cursor.execute(querysongs, (song_id,))
    songsrow = cursor.fetchone()
    if songsrow:
        songs = {
            'id_lagu': songsrow[0],
            'judul_lagu': songsrow[1],
            'genre_lagu': songsrow[2],
            'nama_penyanyi': songsrow[3],
            'penulis_lagu': songsrow[4],
            'durasi_lagu': songsrow[5],
            'tanggal_rilis_lagu': songsrow[6],
            'tahun_rilis_lagu': songsrow[7],
            'total_dimainkan': songsrow[8],
            'total_download': songsrow[9],
            'judul_album': songsrow[10],
        }
    else:
        songs = []
    cursor.close()
    conn.close()
    return render(request, 'playsong.html', {'songs': songs , 'is_premium' : is_premium})

def is_user_premium(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    query_premium = """
        SELECT EXISTS(
             SELECT 1 FROM PREMIUM WHERE email = %s
        )
        """
    cursor.execute(query_premium, (email,))
    is_premium = cursor.fetchone()[0]
    conn.close()
    return is_premium

def add_song_to_playlist_with_option(request, song_id):
    if request.method == 'POST':
        playlist_id = request.POST['playlist_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM PLAYLIST_SONG WHERE id_playlist = %s AND id_song = %s", (playlist_id, song_id))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO PLAYLIST_SONG (id_playlist, id_song) VALUES (%s, %s)", (playlist_id, song_id))
            conn.commit()
            messages.success(request, 'Lagu berhasil ditambahkan ke playlist.')
        else:
            messages.error(request, 'Lagu sudah ada di playlist.')
        cursor.close()
        conn.close()
        return redirect('albums:playlist_detail', playlist_id=playlist_id)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    email = request.session.get('email')
    cursor.execute("SELECT id_playlist, judul FROM USER_PLAYLIST WHERE email_pembuat = %s ", (email,))
    playlistsrow = cursor.fetchall()
    playlists = [{'id_playlist': row[0], 'nama_playlist': row[1]} for row in playlistsrow]
    
    querysongs = """
    SELECT 
    K.id AS "id_lagu",
    K.judul AS "judul_lagu",
    ARRAY_AGG(DISTINCT G.genre) AS "genre_lagu",
    A1.nama AS "nama_penyanyi",
    ARRAY_AGG(DISTINCT A2.nama) AS "penulis_lagu",
    K.durasi AS "durasi_lagu",
    K.tanggal_rilis AS "tanggal_rilis_lagu",
    K.tahun AS "tahun_rilis_lagu",
    S.total_play AS "total_dimainkan",
    S.total_download AS "total_download",
    COALESCE(AL.judul, 'Unknown') AS "judul_album"
    FROM 
        SONG S
    JOIN 
        KONTEN K ON S.id_konten = K.id
    LEFT JOIN 
        ALBUM AL ON S.id_album = AL.id
    JOIN 
        ARTIST AR ON S.id_artist = AR.id
    JOIN 
        AKUN A1 ON AR.email_akun = A1.email
    LEFT JOIN 
        SONGWRITER_WRITE_SONG SWS ON S.id_konten = SWS.id_song
    LEFT JOIN 
        SONGWRITER SW ON SWS.id_songwriter = SW.id
    LEFT JOIN 
        AKUN A2 ON SW.email_akun = A2.email
    LEFT JOIN 
        GENRE G ON K.id = G.id_konten
    WHERE 
        K.id = %s
    GROUP BY 
        K.id, K.judul, A1.nama, K.durasi, K.tanggal_rilis, K.tahun, S.total_play, S.total_download, AL.judul;
    """
    cursor.execute(querysongs, (song_id,))
    songsrow = cursor.fetchone()
    if songsrow:
        songs = [{
            'id_lagu': songsrow[0],
            'judul_lagu': songsrow[1],
            'genre_lagu': songsrow[2],
            'nama_penyanyi': songsrow[3],
            'penulis_lagu': songsrow[4],
            'durasi_lagu': songsrow[5],
            'tanggal_rilis_lagu': songsrow[6],
            'tahun_rilis_lagu': songsrow[7],
            'total_dimainkan': songsrow[8],
            'total_download': songsrow[9],
            'judul_album': songsrow[10],
        }]
    else:
        songs = []
    cursor.close()
    conn.close()
    
    return render(request, 'addsongtoplaylist2.html', {'playlists': playlists, 'songs': songs})

def download_song(request, song_id):
    email = request.session.get('email')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id_song FROM DOWNLOADED_SONG WHERE id_song = %s AND email_downloader = %s", (song_id, email))
        if cursor.fetchone():
            messages.error(request, 'Lagu ini sudah pernah Anda download.')
        else:
            cursor.execute("INSERT INTO DOWNLOADED_SONG (id_song, email_downloader) VALUES (%s, %s)", (song_id, email))
            conn.commit()
            messages.success(request, 'Lagu berhasil didownload.')
    except Exception as e:
        conn.rollback()
        messages.error(request, f'Gagal mendownload lagu: {str(e)}')
    finally:
        cursor.close()
        conn.close()

    return redirect('albums:play_song', song_id=song_id)

def delete_song_from_playlist(request, playlist_id, song_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM PLAYLIST_SONG 
                WHERE id_playlist = %s AND id_song = %s
            """, [playlist_id, song_id])
        messages.success(request, "Lagu berhasil dihapus dari playlist.")
    except Exception as e:
        messages.error(request, "Gagal menghapus lagu dari playlist: " + str(e))
    
    return redirect('albums:playlist_detail', playlist_id = playlist_id)

def play_user_playlist(request, playlist_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve playlist details
    query_playlist = """
        SELECT id_playlist, judul, email_pembuat, jumlah_lagu, total_durasi, tanggal_dibuat, deskripsi, id_user_playlist
        FROM USER_PLAYLIST
        WHERE id_playlist = %s;
    """
    cursor.execute(query_playlist, (playlist_id,))
    playlist_row = cursor.fetchone()

    if playlist_row:
        playlist = {
            'id': playlist_row[0],
            'judul': playlist_row[1],
            'email_pembuat': playlist_row[2],
            'jumlah_lagu': playlist_row[3],
            'total_durasi': playlist_row[4],
            'tanggal_dibuat': playlist_row[5],
            'deskripsi': playlist_row[6],
            'id_user_playlist': playlist_row[7]
        }
        query_songs = """
            SELECT SONG.id_konten AS id_lagu,
                   KONTEN.judul AS judul_lagu,
                   KONTEN.durasi AS durasi_lagu,
                   AKUN.nama AS nama_penyanyi
            FROM USER_PLAYLIST
            JOIN PLAYLIST_SONG ON USER_PLAYLIST.id_playlist = PLAYLIST_SONG.id_playlist
            JOIN SONG ON PLAYLIST_SONG.id_song = SONG.id_konten
            JOIN KONTEN ON SONG.id_konten = KONTEN.id
            JOIN ARTIST ON SONG.id_artist = ARTIST.id
            JOIN AKUN ON ARTIST.email_akun = AKUN.email
            WHERE USER_PLAYLIST.id_playlist = %s;
        """
        cursor.execute(query_songs, (playlist_id,))
        songs_rows = cursor.fetchall()

        songs = [{
            'id_lagu': row[0],
            'judul_lagu': row[1],
            'durasi_lagu': row[2],
            'nama_penyanyi': row[3]
        } for row in songs_rows]
    else:
        songs = []

    cursor.close()
    conn.close()

    return render(request, 'playuserplaylist.html', {'playlist': playlist, 'songs': songs})

def shuffle_play(request, id_user_playlist):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    email_pemain = request.session.get('email')
    timestamp = datetime.now()
    
    cari_email_pembuat = """
        SELECT email_pembuat
        FROM USER_PLAYLIST
        WHERE id_user_playlist = %s
    """
    
    cursor.execute(cari_email_pembuat, (id_user_playlist,))
    email_pembuat = cursor.fetchone()[0]
    
    cursor.execute("INSERT INTO AKUN_PLAY_USER_PLAYLIST (email_pemain, id_user_playlist, waktu, email_pembuat) VALUES (%s, %s, %s, %s)", 
                   (email_pemain, id_user_playlist, timestamp, email_pembuat))
    
    messages.success(request, 'Lagu berhasil dimainkan.')
    
    cari_playlist_id = """
        SELECT id_playlist
        FROM USER_PLAYLIST
        WHERE id_user_playlist = %s
    """
        
    cursor.execute(cari_playlist_id, (id_user_playlist,))
    playlist_id = cursor.fetchone()[0]

    update_play_lagu = """
        UPDATE SONG
        SET total_play = total_play + 1
        WHERE id_konten IN (
            SELECT id_song
            FROM PLAYLIST_SONG
            WHERE id_playlist = %s
        );
    """
    cursor.execute(update_play_lagu, (playlist_id,))
    
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('albums:play_user_playlist', playlist_id=playlist_id)

