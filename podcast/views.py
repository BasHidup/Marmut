from django.shortcuts import render
import main.function as sql
from django.shortcuts import redirect
from uuid import uuid4
from datetime import date
import random

def play_podcast(request, id):

    data = {
        'episode':[],
        'podcast':[],
        'podcast_genre':''
    }
    
    eps = sql.query_result(f'''
        select judul, durasi, tanggal_rilis, deskripsi
        from episode
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
    FROM KONTEN K
    JOIN PODCAST P ON K.id = P.id_konten
    JOIN AKUN A ON A.email = P.email_podcaster
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
    FROM KONTEN K
    JOIN GENRE G ON G.id_konten = K.id
    WHERE K.ID = '{id}'
    ''')     

    string = ""
    for row in genre:
        string += row[0] + ", "

    data['podcast_genre'] = string[:-2]

    print(data['podcast'][0])
    return render(request, 'play_podcast.html', data)

def list_podcast(request, email='kimberlydouglas@hotmail.com'):
    data = {
            'podcast':[],
            'email':"kimberlydouglas@hotmail.com"
        }

    podcast = sql.query_result(f'''
    SELECT K.judul, K.durasi, count(E) as jumlah_episode, K.id, P.EMAIL_PODCASTER
    FROM KONTEN K
    LEFT JOIN EPISODE E ON E.ID_KONTEN_PODCAST = K.ID
    JOIN PODCAST P ON P.ID_KONTEN = K.ID
    WHERE P.EMAIL_PODCASTER = '{data['email']}'
    GROUP BY K.judul, K.durasi,K.id, P.EMAIL_PODCASTER
    ''')

    for row in podcast:
        data['podcast'].append({
            "judul": row[0],
            "durasi":row[1],
            "jumlah_eps": row[2],
            "id":row[3],
        })
    print(data)
    return render(request, 'list_podcast.html', data)

def lihat_episode(request, id):
    data = {
            'episode':[],
        }
    
    eps = sql.query_result(f'''
    SELECT E.judul, E.deskripsi, E.durasi, E.tanggal_rilis, E.id_episode
    FROM EPISODE E
    WHERE E.id_konten_podcast = '{id}'
    ''')
    for row in eps:
            data['episode'].append({
                "judul": row[0],
                "deskripsi": row[1],
                "durasi": row[2],
                "tanggal_rilis": row[3],
                "id_episode":row[4]
            })

    return render(request, 'lihat_episode.html', data)

def home_podcast(request):
    data = {
        'podcast':[],
    }
    podcast = sql.query_result(f'''
    SELECT K.judul, A.nama, K.durasi, P.id_konten
    FROM KONTEN K
    JOIN PODCAST P ON K.id = P.id_konten
    JOIN AKUN A ON A.email = P.email_podcaster
    ''')

    for row in podcast:
        data['podcast'].append({
            "judul": row[0],
            "nama":row[1],
            "durasi": row[2],
            "id":row[3]
        })

    return render(request, 'home_podcast.html', data)

def tambah_episode(request, id):
    data = {
            'podcast':[],
        }

    podcast = sql.query_result(f'''
    SELECT K.judul, K.id
    FROM KONTEN K
    WHERE K.ID = '{id}'
    ''')

    for row in podcast:
        data['podcast'].append({
            "judul": row[0],
            "id":row[1]
        })
    return render(request, 'tambah_episode.html', data)

def form_tambah_episode(request, id):
    if request.method == "POST":
        id_episode = uuid4()
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')
        durasi = int(request.POST.get('durasi'))
        tanggal_buat = date.today().strftime('%Y-%m-%d')

        sql.query_add(
            f"""
            INSERT INTO EPISODE(id_episode, id_konten_podcast, judul, deskripsi, durasi, tanggal_rilis)
            VALUES(
                '{id_episode}',
                '{id}',
                '{judul}',
                '{deskripsi}',
                '{durasi}',
                '{tanggal_buat}'    
            );
            """
        )

        return redirect('podcast:lihat_episode', id=id)

def tambah_podcast(request, email):
    data = {
            'email':email,
            'genre':[]
        }
    
    genre = sql.query_result(f'''
    SELECT DISTINCT G.GENRE
    FROM GENRE G
    ''')

    for row in genre:
        data['genre'].append({
            "genre": row[0],
        })
    return render(request, 'tambah_podcast.html', data)

def form_tambah_podcast(request, email):
    if request.method == "POST":
        id_konten = uuid4()
        judul = request.POST.get('judul')
        genre = request.POST.getlist('genre')
        durasi = 0
        tahun = random.randint(2000, 2024)
        tanggal_buat = date.today().strftime('%Y-%m-%d')

        sql.query_add(
            f"""
            INSERT INTO KONTEN(id, judul, tanggal_rilis, tahun, durasi)
            VALUES(
                '{id_konten}',
                '{judul}',
                '{tanggal_buat}',
                '{tahun}',
                '{durasi}'
            );
            """
        )
        sql.query_add(
            f"""
            INSERT INTO PODCAST(id_konten, email_podcaster)
            VALUES(
                '{id_konten}',
                '{email}'  
            );
            """
        )
        for g in genre:
            sql.query_add(
                f"""
                INSERT INTO GENRE(id_konten, genre)
                VALUES(
                    '{id_konten}',
                    '{g}'  
                );
                """
            )
        return redirect('podcast:list_podcast')
    
#def edit_podcast(request, id):
    data = {
            'id':id,
            'genre':[]
        }
    
    genre = sql.query_result(f'''
    SELECT DISTINCT G.GENRE
    FROM GENRE G
    ''')

    for row in genre:
        data['genre'].append({
            "genre": row[0],
        })
    return render(request, 'edit_podcast.html', data)

#def form_edit_podcast(request, id):

    if request.method == "POST":
        judul = request.POST.get('judul')
        genre = request.POST.getlist('genre')

        sql.query_add(
            f"""
            UPDATE KONTEN
            SET judul='{judul}'
            WHERE id='{id}';
            );
            """
        )

        sql.query_add(
            f"""
            DELETE FROM GENRE WHERE id_konten='{id}';
            """
        )

        for g in genre:
            sql.query_add(
                f"""
                INSERT INTO GENRE(id_konten, genre)
                VALUES(
                    '{id}',
                    '{g}'  
                );
                """
            )

        return redirect('podcast:list_podcast')
    
def delete_episode(request, id_episode):
    print(id_episode)
    res = sql.query_result(f'''
    SELECT E.id_konten_podcast 
    FROM EPISODE E
    where E.id_episode = '{id_episode}'
    ''')

    for row in res:
        id = row[0]

    sql.query_add(
            f"""
            DELETE FROM EPISODE WHERE id_episode='{id_episode}';
            """
        )
    
    return redirect('podcast:lihat_episode', id=id)

def delete_podcast(request, id):
    sql.query_add(
            f"""
            DELETE FROM KONTEN WHERE id='{id}';
            """
        )
    
    return redirect('podcast:home_podcast')