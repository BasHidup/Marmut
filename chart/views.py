from django.shortcuts import render
import main.function as sql

def home_chart(request):
    data = {
            'chart':[],
        }

    chart = sql.query_result(f'''
    SELECT c.tipe, c.id_playlist
    FROM CHART C
    ''')

    for row in chart:
        data['chart'].append({
            "tipe": row[0],
            "id": row[1]
        })

    return render(request, 'home_chart.html', data)

def detail_chart(request, id):
    data = {
            'chart':[],
            'song':[]
        }
    
    chart = sql.query_result(f'''
    SELECT c.tipe
    FROM CHART C
    WHERE id_playlist = '{id}'
    ''')

    for row in chart:
        data['chart'].append({
            "tipe": row[0],
        })

    song = sql.query_result(f'''
    SELECT K.judul, A.NAMA, K.tanggal_rilis, S.total_play, PS.id_playlist
    FROM KONTEN K
    JOIN SONG S ON S.id_konten = K.id
    JOIN PLAYLIST_SONG PS ON PS.id_song = K.id
    JOIN ARTIST AT ON AT.id = S.id_artist
    JOIN AKUN A ON AT.email_akun = A.email
    WHERE PS.id_playlist = '{id}'
    ''')

    for row in song:
        data['song'].append({
            "judul": row[0],
            "nama": row[1],
            "tanggal_rilis": row[2],
            "total_play": row[3],
            "id_song": row[4]

        })
    
    return render(request, 'detail_chart.html', data)