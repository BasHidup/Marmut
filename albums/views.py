from uuid import uuid4
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
import psycopg2
from django.http import HttpResponse
from django.template import loader

from albums.models import DownloadedSong

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
