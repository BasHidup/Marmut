# views.py
import psycopg2
from django.http import HttpResponse
from django.template import loader

def daftar_episode(request, id_konten):
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="6666",
        host="localhost",
        port="5432",
        options="-c search_path=marmut"
    )
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT podcast.judul, episode.durasi, episode.tanggal_rilis, episode.deskripsi 
                   FROM podcast, episode 
                   WHERE podcast.id_konten = %s;''', (id_konten,))
    records = cursor.fetchall()

    daftar_episode = []
    for row in records:
        daftar_episode.append({
            'judul_podcast': row[0],
            'durasi': row[1],
            'tanggal_rilis': row[2],
            'deskripsi': row[3]
        })

    conn.close()

    template = loader.get_template('Play Podcast.html')
    context = {'daftar_episode': daftar_episode}
    return HttpResponse(template.render(context, request))
