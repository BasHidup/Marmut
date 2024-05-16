from django.shortcuts import render
import main.function as sql

def play_podcast(request, id):

    data = {
        'episode':[],
        'podcast':[],
        'podcast_genre':''
    }
    
    eps = sql.query_result(f'''
        select judul, durasi, tanggal_rilis, deskripsi
        from marmut.episode
        where id_konten_podcast = '{id}';
        ''')

    for row in eps:
        data['episode'].append({
            "judul": row[0],
            "durasi": row[1],
            "tanggal_rilis": row[2],
            "deskripsi": row[3],
        })

    podcast = sql.query_result(f'''
    SELECT K.judul, A.nama, K.durasi, K.tanggal_rilis, K.tahun
    FROM marmut.KONTEN K
    JOIN marmut.PODCAST P ON K.id = P.id_konten
    JOIN marmut.AKUN A ON A.email = P.email_podcaster
    WHERE K.ID = '{id}'
    ''')

    for row in podcast:
        data['podcast'].append({
            "judul": row[0],
            "nama":row[1],
            "durasi": row[2],
            "tanggal_rilis": row[3],
            "tahun": row[4],
        })
        
    genre = sql.query_result(f'''
    SELECT G.GENRE
    FROM marmut.KONTEN K
    JOIN marmut.GENRE G ON G.id_konten = K.id
    WHERE K.ID = '{id}'
    ''')     

    string = ""
    for row in genre:
        string += row[0] + ", "

    data['podcast_genre'] = string[:-2]

    print(data['podcast'][0])
    return render(request, 'play_podcast.html', data)

def list_podcast(request, id):
    data = {
            'podcast':[],
        }

    podcast = sql.query_result(f'''
    SELECT K.judul, A.NAMA, K.tanggal_rilis, S.total_play, PS.id_playlist
    FROM KONTEN K
    JOIN SONG S ON S.id_konten = K.id
    JOIN PLAYLIST_SONG PS ON PS.id_song = K.id
    JOIN ARTIST AT ON AT.id = S.id_artist
    JOIN AKUN A ON AT.email_akun = A.email
    WHERE PS.id_playlist = '{id}'
    ''')

    for row in podcast:
        data['podcast'].append({
            "judul": row[0],
            "durasi":row[1],
            "jumlah_eps": row[2],
            "id":row[3]
        })

    return render(request, 'list_podcast.html', data)

def lihat_episode(request, id):
    data = {
            'episode':[],
        }
    
    eps = sql.query_result(f'''
    SELECT E.judul, E.deskripsi, E.durasi, E.tanggal_rilis
    FROM marmut.EPISODE E
    WHERE E.id_konten_podcast = '{id}'
    ''')
    for row in eps:
            data['episode'].append({
                "judul": row[0],
                "deskripsi": row[1],
                "durasi": row[2],
                "tanggal_rilis": row[3],
            })

    return render(request, 'lihat_episode.html', data)

def home_podcast(request):
    data = {
        'podcast':[],
    }
    podcast = sql.query_result(f'''
    SELECT K.judul, A.nama, K.durasi, P.id_konten
    FROM marmut.KONTEN K
    JOIN marmut.PODCAST P ON K.id = P.id_konten
    JOIN marmut.AKUN A ON A.email = P.email_podcaster
    ''')

    for row in podcast:
        data['podcast'].append({
            "judul": row[0],
            "nama":row[1],
            "durasi": row[2],
            "id":row[3]
        })

    return render(request, 'home_podcast.html', data)