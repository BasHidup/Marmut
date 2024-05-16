from datetime import datetime
from uuid import uuid4
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
import psycopg2
from django.http import HttpResponse
from django.template import loader

from albums.models import DownloadedSong

def has_logged_in(request):
    if request.session['email'] == 'not found' or request.session['roles'] == 'not found':
        return False
    
    return True

def show_albums(request):
    if(not has_logged_in(request)):
        return redirect('authentication:login_view')

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
    if(not has_logged_in(request)):
        return redirect('authentication:login_view')
    
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

    print("akun artist: ", akun_ar)
    print("akun sw: ", akun_sw)
    print("artists", artists)
    print("sws:", songwriter)
    print("genre: ", genres)

    context = {
        'akun_ar':akun_ar,
        'akun_sw':akun_sw,
        'artists':artists,
        'songwriters':songwriter,
        'genres':genres,
        'labels':labels,
    }

    return render(request, "create_album.html", context)

def show_songs(request, id_album):
    if(not has_logged_in(request)):
        return redirect('authentication:login_view')
    
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
    print(id_album_ini)
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
    print(songs)

    context = {
        'album_name':album_name,
        'id_album':id_album_ini,
        'songs':songs,
        'label_acc':label_acc,
    }

    return render(request, "list_songs.html", context)

def create_song(request, id_album):
    if(not has_logged_in(request)):
        return redirect('authentication:login_view')
    
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

    print("akun artist: ", akun_ar)
    print("akun sw: ", akun_sw)
    print("id_album: ", id_album)
    print("nama album: ", album_name)
    print("artists", artists)
    print("sws:", songwriter)
    print("genre: ", genres)

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
    if(not has_logged_in(request)):
        return redirect('authentication:login_view')
    
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
    print(song)
    
    label_acc = None
    # songs = [
    #     {'id_konten':'bb6dd4b7-d706-4b59-aaee-0fdfce057c0a', 'judul':'Bite Me', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'total_play':1678433, 'total_download':638350, 'judul_album':'Dark Blood', 'durasi':3},
    #     {'id_konten':'381a697a-ca46-4072-8ad4-6287a890502a', 'judul':'Next Level', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'total_play':2924981, 'total_download':584208, 'judul_album':'Savage - The 1st Mini Album', 'durasi':3},
    #     {'id_konten':'7712c805-4ecc-4e89-89c0-6d117b911137', 'judul':'Sacrifice (Eat Me Up)', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'total_play':4966922, 'total_download':573150, 'judul_album':'Dark Blood', 'durasi':4},
    #     {'id_konten':'6fc5d6c1-5bbc-455d-8fb3-d5ff41b118ba', 'judul':'Savage', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'total_play':4340261, 'total_download':847948, 'judul_album':'Savage - The 1st Mini Album', 'durasi':5},
    #     {'id_konten':'8ed949e6-6655-4bc0-8bfb-fbc942790791', 'judul':'Darari', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'total_play':1220369, 'total_download':142110, 'judul_album':'THE SECOND STEP : CHAPTER ONE', 'durasi':3},
    #     {'id_konten':'313d94d4-be1f-408a-84b9-7428a459efc9', 'judul':'S-CLASS', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'c51e1dfb-b7dc-4914-8646-2550948cc275', 'total_play':1496496, 'total_download':642167, 'judul_album':'5-STAR', 'durasi':2},
    #     {'id_konten':'ceb16047-d196-4423-bafa-b4b8de60e3c7', 'judul':'ELEVEN', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'cd808adc-e301-4766-afc0-42a1b54c6781', 'total_play':2527722, 'total_download':309456, 'judul_album':'I\'VE MINE', 'durasi':3},
    #     {'id_konten':'919ef45f-2796-4354-90f5-d70dc87a445e', 'judul':'JIKJIN', 'artist':'556079db-acbc-4472-93f0-d0851a1ce2a0', 'id_album':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'total_play':4147755, 'total_download':429754, 'judul_album':'THE SECOND STEP : CHAPTER ONE', 'durasi':4},
    #     {'id_konten':'ca1eebd0-46ac-4386-acac-6e2409cf639f', 'judul':'God\'s Menu', 'artist':'556079db-acbc-4472-93f0-d0851a1ce2a0', 'id_album':'c51e1dfb-b7dc-4914-8646-2550948cc275', 'total_play':2149343, 'total_download':572258, 'judul_album':'5-STAR', 'durasi':2},
    #     {'id_konten':'86b1eeed-a5f4-49b0-a5e1-e2d89915f7ec', 'judul':'Love Dive', 'artist':'556079db-acbc-4472-93f0-d0851a1ce2a0', 'id_album':'cd808adc-e301-4766-afc0-42a1b54c6781', 'total_play':2184480, 'total_download':477026, 'judul_album':'I\'VE MINE', 'durasi':3},
    # ]

    # selected_song = [song for song in songs if song['id_konten'] == id_song][0]

    context = {
        'song':song,
        'label_acc':label_acc,
    }

    return render(request, 'song_detail.html', context)

def downloaded_songs(request):
    songs = DownloadedSong.objects.filter(user=request.user)  
    return render(request, 'downloaded_songs.html', {'songs': songs})

def delete_downloaded_song(request, song_id):
    song = get_object_or_404(DownloadedSong, id=song_id, user=request.user)
    if request.method == 'POST':
        song_title = song.title  # Menyimpan judul untuk message
        song.delete()
        messages.success(request, f'Berhasil menghapus Lagu dengan judul "{song_title}" dari daftar unduhan!')
        return redirect('downloaded_songs')
