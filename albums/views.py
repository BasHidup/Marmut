from datetime import datetime, timezone
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

def show_albums(request):
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
    if request.method == 'POST':
        judul = request.POST.get('judul')
        print(judul)
        id_label = request.POST.get('id_label')
        print(id_label)

        # Validasi data, misalnya pastikan judul tidak kosong
        if not judul:
            return render(request, 'create_album.html', {'error': 'Judul tidak boleh kosong'})
        
        # Generate UUID untuk id album baru
        id_album = uuid4()

        # Query untuk insert data album baru ke tabel ALBUM
        query = f"INSERT INTO ALBUM (id, judul, jumlah_lagu, id_label, total_durasi) VALUES ('{id_album}', '{judul}', 0, '{id_label}', 0);"

        try:
            with connection.cursor() as cursor:
                cursor.execute('SET search_path TO public')
                cursor.execute(query)
        except Exception as e:
            # Handle error
            return render(request, 'create_album.html', {'error': str(e)})

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


    context = {
        'labels':labels,
    }

    return render(request, "create_album.html", context)

def show_songs(request, id_album):
    id_album_ini = id_album
    # label_acc = {'label':'HYBE'}
    label_acc = None
    albums = [
        {'id':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'judul':'Dark Blood', 'jumlah_lagu':11, 'label':'HYBE', 'total_durasi':37},
        {'id':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'judul':'Savage - The 1st Mini Album', 'jumlah_lagu':9, 'label':'SM', 'total_durasi':27},
        {'id':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'judul':'THE SECOND STEP : CHAPTER ONE', 'jumlah_lagu':8, 'label':'YG', 'total_durasi':25},
        {'id':'c51e1dfb-b7dc-4914-8646-2550948cc275', 'judul':'5-STAR', 'jumlah_lagu':12, 'label':'JYP', 'total_durasi':48},
        {'id':'cd808adc-e301-4766-afc0-42a1b54c6781', 'judul':'I\'VE MINE', 'jumlah_lagu':10, 'label':'Starship', 'total_durasi':33}
    ]
    songs = [
        {'id_konten':'bb6dd4b7-d706-4b59-aaee-0fdfce057c0a', 'judul':'Bite Me', 'id_artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'total_play':1678433, 'total_download':638350, 'judul_album':'Dark Blood', 'durasi':3},
        {'id_konten':'381a697a-ca46-4072-8ad4-6287a890502a', 'judul':'Next Level', 'id_artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'total_play':2924981, 'total_download':584208, 'judul_album':'Savage - The 1st Mini Album', 'durasi':3},
        {'id_konten':'7712c805-4ecc-4e89-89c0-6d117b911137', 'judul':'Sacrifice (Eat Me Up)', 'id_artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'total_play':4966922, 'total_download':573150, 'judul_album':'Dark Blood', 'durasi':4},
        {'id_konten':'6fc5d6c1-5bbc-455d-8fb3-d5ff41b118ba', 'judul':'Savage', 'id_artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'total_play':4340261, 'total_download':847948, 'judul_album':'Savage - The 1st Mini Album', 'durasi':5},
        {'id_konten':'8ed949e6-6655-4bc0-8bfb-fbc942790791', 'judul':'Darari', 'id_artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'total_play':1220369, 'total_download':142110, 'judul_album':'THE SECOND STEP : CHAPTER ONE', 'durasi':3},
        {'id_konten':'313d94d4-be1f-408a-84b9-7428a459efc9', 'judul':'S-CLASS', 'id_artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'c51e1dfb-b7dc-4914-8646-2550948cc275', 'total_play':1496496, 'total_download':642167, 'judul_album':'5-STAR', 'durasi':2},
        {'id_konten':'ceb16047-d196-4423-bafa-b4b8de60e3c7', 'judul':'ELEVEN', 'id_artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'cd808adc-e301-4766-afc0-42a1b54c6781', 'total_play':2527722, 'total_download':309456, 'judul_album':'I\'VE MINE', 'durasi':3},
        {'id_konten':'919ef45f-2796-4354-90f5-d70dc87a445e', 'judul':'JIKJIN', 'id_artist':'556079db-acbc-4472-93f0-d0851a1ce2a0', 'id_album':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'total_play':4147755, 'total_download':429754, 'judul_album':'THE SECOND STEP : CHAPTER ONE', 'durasi':4},
        {'id_konten':'ca1eebd0-46ac-4386-acac-6e2409cf639f', 'judul':'God\'s Menu', 'id_artist':'556079db-acbc-4472-93f0-d0851a1ce2a0', 'id_album':'c51e1dfb-b7dc-4914-8646-2550948cc275', 'total_play':2149343, 'total_download':572258, 'judul_album':'5-STAR', 'durasi':2},
        {'id_konten':'86b1eeed-a5f4-49b0-a5e1-e2d89915f7ec', 'judul':'Love Dive', 'id_artist':'556079db-acbc-4472-93f0-d0851a1ce2a0', 'id_album':'cd808adc-e301-4766-afc0-42a1b54c6781', 'total_play':2184480, 'total_download':477026, 'judul_album':'I\'VE MINE', 'durasi':3},
    ]

    filtered_songs = [song for song in songs if song['id_album'] == id_album_ini]
    album_name = next((album['judul'] for album in albums if album['id'] == id_album_ini), None)

    context = {
        'album_name':album_name,
        'id_album':id_album_ini,
        'songs':filtered_songs,
        'label_acc':label_acc,
    }

    return render(request, "list_songs.html", context)

def create_song(request, id_album):
    logged_in = {'jenis_akun':'artist', 'name':'Jessica Brown'}
    id_album_ini = id_album
    albums = [
        {'id':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'judul':'Dark Blood', 'jumlah_lagu':11, 'label':'HYBE', 'total_durasi':37},
        {'id':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'judul':'Savage - The 1st Mini Album', 'jumlah_lagu':9, 'label':'SM', 'total_durasi':27},
        {'id':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'judul':'THE SECOND STEP : CHAPTER ONE', 'jumlah_lagu':8, 'label':'YG', 'total_durasi':25},
        {'id':'c51e1dfb-b7dc-4914-8646-2550948cc275', 'judul':'5-STAR', 'jumlah_lagu':12, 'label':'JYP', 'total_durasi':48},
        {'id':'cd808adc-e301-4766-afc0-42a1b54c6781', 'judul':'I\'VE MINE', 'jumlah_lagu':10, 'label':'Starship', 'total_durasi':33}
    ]
    artists = [
        {'name':'Kathleen Jackson'},
        {'name':'John Smith'},
        {'name':'Emily Johnson'},
        {'name':'Michael Davis'},
        {'name':'Jessica Brown'},
        {'name':'Daniel Martinez'},
    ]
    songwriter = [
        {'name':'Daniel Martinez'},
        {'name':'Sophia Garcia'},
        {'name':'William Wilson'},
        {'name':'Isabella Anderson'},
        {'name':'James Taylor'},
        {'name':'Olivia Thomas'},
        {'name':'Ethan Hernandez'}
    ]
    genres = [
        {'jenis': 'R&B'},
        {'jenis': 'Pop'},
        {'jenis': 'Rock'},
        {'jenis': 'Hip Hop'},
        {'jenis': 'Electronic'},
    ]

    album_name = next((album['judul'] for album in albums if album['id'] == id_album_ini), None)
    context = {
        'logged_in':logged_in,
        'id_album':id_album,
        'album_name':album_name,
        'artists':artists,
        'songwriters':songwriter,
        'genres':genres,
    }

    return render(request, 'create_song.html', context)

def edit_album(request, id_album):
    albums = [
        {'id':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'judul':'Dark Blood', 'jumlah_lagu':11, 'label':'HYBE', 'total_durasi':37},
        {'id':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'judul':'Savage - The 1st Mini Album', 'jumlah_lagu':9, 'label':'SM', 'total_durasi':27},
        {'id':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'judul':'THE SECOND STEP : CHAPTER ONE', 'jumlah_lagu':8, 'label':'YG', 'total_durasi':25},
        {'id':'c51e1dfb-b7dc-4914-8646-2550948cc275', 'judul':'5-STAR', 'jumlah_lagu':12, 'label':'JYP', 'total_durasi':48},
        {'id':'cd808adc-e301-4766-afc0-42a1b54c6781', 'judul':'I\'VE MINE', 'jumlah_lagu':10, 'label':'Starship', 'total_durasi':33}
    ]
    label = [
        {'name':'HYBE'},
        {'name':'SM'},
        {'name':'YG'},
        {'name':'JYP'},
        {'name':'Starship'},
    ]

    selected_album = [album for album in albums if album['id'] == id_album][0]

    context = {
        'album' : selected_album,
        'labels' : label,
    }

    return render(request, 'edit_album.html', context)

def show_song_detail(request, id_song):
    # label_acc = {'label':'HYBE'}
    label_acc = None
    songs = [
        {'id_konten':'bb6dd4b7-d706-4b59-aaee-0fdfce057c0a', 'judul':'Bite Me', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'total_play':1678433, 'total_download':638350, 'judul_album':'Dark Blood', 'durasi':3},
        {'id_konten':'381a697a-ca46-4072-8ad4-6287a890502a', 'judul':'Next Level', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'total_play':2924981, 'total_download':584208, 'judul_album':'Savage - The 1st Mini Album', 'durasi':3},
        {'id_konten':'7712c805-4ecc-4e89-89c0-6d117b911137', 'judul':'Sacrifice (Eat Me Up)', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'total_play':4966922, 'total_download':573150, 'judul_album':'Dark Blood', 'durasi':4},
        {'id_konten':'6fc5d6c1-5bbc-455d-8fb3-d5ff41b118ba', 'judul':'Savage', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'total_play':4340261, 'total_download':847948, 'judul_album':'Savage - The 1st Mini Album', 'durasi':5},
        {'id_konten':'8ed949e6-6655-4bc0-8bfb-fbc942790791', 'judul':'Darari', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'total_play':1220369, 'total_download':142110, 'judul_album':'THE SECOND STEP : CHAPTER ONE', 'durasi':3},
        {'id_konten':'313d94d4-be1f-408a-84b9-7428a459efc9', 'judul':'S-CLASS', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'c51e1dfb-b7dc-4914-8646-2550948cc275', 'total_play':1496496, 'total_download':642167, 'judul_album':'5-STAR', 'durasi':2},
        {'id_konten':'ceb16047-d196-4423-bafa-b4b8de60e3c7', 'judul':'ELEVEN', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'cd808adc-e301-4766-afc0-42a1b54c6781', 'total_play':2527722, 'total_download':309456, 'judul_album':'I\'VE MINE', 'durasi':3},
        {'id_konten':'919ef45f-2796-4354-90f5-d70dc87a445e', 'judul':'JIKJIN', 'artist':'556079db-acbc-4472-93f0-d0851a1ce2a0', 'id_album':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'total_play':4147755, 'total_download':429754, 'judul_album':'THE SECOND STEP : CHAPTER ONE', 'durasi':4},
        {'id_konten':'ca1eebd0-46ac-4386-acac-6e2409cf639f', 'judul':'God\'s Menu', 'artist':'556079db-acbc-4472-93f0-d0851a1ce2a0', 'id_album':'c51e1dfb-b7dc-4914-8646-2550948cc275', 'total_play':2149343, 'total_download':572258, 'judul_album':'5-STAR', 'durasi':2},
        {'id_konten':'86b1eeed-a5f4-49b0-a5e1-e2d89915f7ec', 'judul':'Love Dive', 'artist':'556079db-acbc-4472-93f0-d0851a1ce2a0', 'id_album':'cd808adc-e301-4766-afc0-42a1b54c6781', 'total_play':2184480, 'total_download':477026, 'judul_album':'I\'VE MINE', 'durasi':3},
    ]

    selected_song = [song for song in songs if song['id_konten'] == id_song][0]

    context = {
        'song':selected_song,
        'label_acc':label_acc,
    }

    return render(request, 'song_detail.html', context)

def edit_song(request, id_song):
    albums = [
        {'id':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'judul':'Dark Blood', 'jumlah_lagu':11, 'label':'HYBE', 'total_durasi':37},
        {'id':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'judul':'Savage - The 1st Mini Album', 'jumlah_lagu':9, 'label':'SM', 'total_durasi':27},
        {'id':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'judul':'THE SECOND STEP : CHAPTER ONE', 'jumlah_lagu':8, 'label':'YG', 'total_durasi':25},
        {'id':'c51e1dfb-b7dc-4914-8646-2550948cc275', 'judul':'5-STAR', 'jumlah_lagu':12, 'label':'JYP', 'total_durasi':48},
        {'id':'cd808adc-e301-4766-afc0-42a1b54c6781', 'judul':'I\'VE MINE', 'jumlah_lagu':10, 'label':'Starship', 'total_durasi':33}
    ]
    songs = [
        {'id_konten':'bb6dd4b7-d706-4b59-aaee-0fdfce057c0a', 'judul':'Bite Me', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'total_play':1678433, 'total_download':638350, 'judul_album':'Dark Blood', 'durasi':3},
        {'id_konten':'381a697a-ca46-4072-8ad4-6287a890502a', 'judul':'Next Level', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'total_play':2924981, 'total_download':584208, 'judul_album':'Savage - The 1st Mini Album', 'durasi':3},
        {'id_konten':'7712c805-4ecc-4e89-89c0-6d117b911137', 'judul':'Sacrifice (Eat Me Up)', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'total_play':4966922, 'total_download':573150, 'judul_album':'Dark Blood', 'durasi':4},
        {'id_konten':'6fc5d6c1-5bbc-455d-8fb3-d5ff41b118ba', 'judul':'Savage', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'total_play':4340261, 'total_download':847948, 'judul_album':'Savage - The 1st Mini Album', 'durasi':5},
        {'id_konten':'8ed949e6-6655-4bc0-8bfb-fbc942790791', 'judul':'Darari', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'total_play':1220369, 'total_download':142110, 'judul_album':'THE SECOND STEP : CHAPTER ONE', 'durasi':3},
        {'id_konten':'313d94d4-be1f-408a-84b9-7428a459efc9', 'judul':'S-CLASS', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'c51e1dfb-b7dc-4914-8646-2550948cc275', 'total_play':1496496, 'total_download':642167, 'judul_album':'5-STAR', 'durasi':2},
        {'id_konten':'ceb16047-d196-4423-bafa-b4b8de60e3c7', 'judul':'ELEVEN', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'cd808adc-e301-4766-afc0-42a1b54c6781', 'total_play':2527722, 'total_download':309456, 'judul_album':'I\'VE MINE', 'durasi':3},
        {'id_konten':'919ef45f-2796-4354-90f5-d70dc87a445e', 'judul':'JIKJIN', 'artist':'556079db-acbc-4472-93f0-d0851a1ce2a0', 'id_album':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'total_play':4147755, 'total_download':429754, 'judul_album':'THE SECOND STEP : CHAPTER ONE', 'durasi':4},
        {'id_konten':'ca1eebd0-46ac-4386-acac-6e2409cf639f', 'judul':'God\'s Menu', 'artist':'556079db-acbc-4472-93f0-d0851a1ce2a0', 'id_album':'c51e1dfb-b7dc-4914-8646-2550948cc275', 'total_play':2149343, 'total_download':572258, 'judul_album':'5-STAR', 'durasi':2},
        {'id_konten':'86b1eeed-a5f4-49b0-a5e1-e2d89915f7ec', 'judul':'Love Dive', 'artist':'556079db-acbc-4472-93f0-d0851a1ce2a0', 'id_album':'cd808adc-e301-4766-afc0-42a1b54c6781', 'total_play':2184480, 'total_download':477026, 'judul_album':'I\'VE MINE', 'durasi':3},
    ]
    artists = [
        {'name':'Kathleen Jackson'},
        {'name':'John Smith'},
        {'name':'Emily Johnson'},
        {'name':'Michael Davis'},
        {'name':'Jessica Brown'},
        {'name':'Daniel Martinez'},
    ]

    selected_song = [song for song in songs if song['id_konten'] == id_song][0]
    album_id = selected_song['id_album']
    album_name = [album['judul'] for album in albums if album['id'] == album_id][0]

    context = {
        'song':selected_song,
        'album_name' : album_name,
        'artists' : artists,
    }

    return render(request, 'edit_song.html', context)


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

