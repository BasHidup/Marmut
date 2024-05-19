from django.shortcuts import render
import main.function as sql
from django.shortcuts import redirect

def has_logged_in(request):
    print(request.session['email'])
    print(request.session['roles'])
    if request.session['email'] == 'not found' or request.session['roles'] == 'not found':
        return False
    
    return True

def home_chart(request):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
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

    data['roles'] = request.session['roles']

    return render(request, 'home_chart.html', data)

def detail_chart(request, id):
    if not has_logged_in(request):
        return redirect('authentication:show_start')
    
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
    SELECT K.judul, A.NAMA, K.tanggal_rilis, S.total_play, PS.id_song
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

    data['roles'] = request.session['roles']
    
    return render(request, 'detail_chart.html', data)