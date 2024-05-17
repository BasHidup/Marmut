from django.shortcuts import render, redirect, get_object_or_404
import psycopg2
from .models import Paket, Transaksi
from django.contrib import messages


# Create your views here.

def show_dashboard(request):
    
    return render(request, 'dashboarduser.html')

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

def show_royalties(request):
    royalties = [
        {'id_pemilik_hak_cipta':'af607859-f8ea-4997-bde2-87c30ed06ba4', 'id_lagu':'bb6dd4b7-d706-4b59-aaee-0fdfce057c0a', 'jumlah':660681840, 'judul':'Bite Me', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'total_play':1678433, 'total_download':638350, 'judul_album':'Dark Blood', 'durasi':3},
        {'id_pemilik_hak_cipta':'01f3ddcf-4fe6-4110-9101-4e5c3255b497', 'id_lagu':'381a697a-ca46-4072-8ad4-6287a890502a', 'jumlah':121371939, 'judul':'Next Level', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'total_play':2924981, 'total_download':584208, 'judul_album':'Savage - The 1st Mini Album', 'durasi':3},
        {'id_pemilik_hak_cipta':'a33451a8-8956-4e4d-afe7-8504385bbf84', 'id_lagu':'7712c805-4ecc-4e89-89c0-6d117b911137', 'jumlah':406952469, 'judul':'Sacrifice (Eat Me Up)', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'d76fd6f2-c7b6-4a34-bdc1-f873c106808f', 'total_play':4966922, 'total_download':573150, 'judul_album':'Dark Blood', 'durasi':4},
        {'id_pemilik_hak_cipta':'68f96fd0-322f-48d2-89c9-8a9732130088', 'id_lagu':'6fc5d6c1-5bbc-455d-8fb3-d5ff41b118ba', 'jumlah':212726460, 'judul':'Savage', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'928a12f8-cf27-48da-89b3-5cb8a365b56a', 'total_play':4340261, 'total_download':847948, 'judul_album':'Savage - The 1st Mini Album', 'durasi':5},
        {'id_pemilik_hak_cipta':'48084a9d-30e6-4f8c-831e-4653d6aea273', 'id_lagu':'8ed949e6-6655-4bc0-8bfb-fbc942790791', 'jumlah':112954143, 'judul':'Darari', 'artist':'0626a456-8575-4ee5-8604-a6034e5787e2', 'id_album':'2e77243b-62f3-4a4a-a5b1-c7bf70f85209', 'total_play':1220369, 'total_download':142110, 'judul_album':'THE SECOND STEP : CHAPTER ONE', 'durasi':3},
    ]

    context = {
        'royalties':royalties,
    }

    return render(request, 'cek_royalti.html', context)


def daftar_paket(request):
    pakets = Paket.objects.all()
    return render(request, 'daftar_paket.html', {'pakets': pakets})

def berlangganan_paket(request, paket_id):
    paket = get_object_or_404(Paket, id=paket_id)
    if request.method == 'POST':
        Transaksi.objects.create(
            user=request.user,
            paket=paket,
            metode_pembayaran=request.POST.get('metode_pembayaran')
        )
        messages.success(request, 'Berhasil berlangganan paket!')
        return redirect('riwayat_transaksi')
    return render(request, 'berlangganan_paket.html', {'paket': paket})

def riwayat_transaksi(request):
    transaksi = Transaksi.objects.filter(user=request.user)
    return render(request, 'riwayat_transaksi.html', {'transaksi': transaksi})

def show_homepage(request):
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
    })
