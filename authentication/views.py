import random
from uuid import uuid4
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

def show_start(request):
    return render(request, 'start.html')

@csrf_exempt
def login_view(request):
    request.session['email'] = 'not found'
    request.session['roles'] = 'not found'

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Query untuk memeriksa di tabel AKUN
        query_akun = f"""
        SELECT email
        FROM AKUN
        WHERE email = '{email}' AND password = '{password}'
        GROUP BY email
        """

        # Query untuk memeriksa di tabel ARTIST
        query_artist = f"""
        SELECT u.email
        FROM AKUN u
        JOIN ARTIST ar ON u.email = ar.email_akun
        WHERE u.email = '{email}' AND u.password = '{password}'
        GROUP BY u.email
        """

        # Query untuk memeriksa di tabel SONGWRITER
        query_songwriter = f"""
        SELECT u.email
        FROM AKUN u
        JOIN SONGWRITER sw ON u.email = sw.email_akun
        WHERE u.email = '{email}' AND u.password = '{password}'
        GROUP BY u.email
        """

        # Query untuk memeriksa di tabel PODCASTER
        query_podcaster = f"""
        SELECT u.email
        FROM AKUN u
        JOIN PODCASTER pc ON u.email = pc.email
        WHERE u.email = '{email}' AND u.password = '{password}'
        GROUP BY u.email
        """

        # Query untuk memeriksa di tabel LABEL
        query_label = f"""
        SELECT
            l.email,
            'label' AS role
        FROM LABEL l
        WHERE l.email = '{email}' AND l.password = '{password}'
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute('SET search_path TO public')

                roles = set()
                email_found = None

                # Cek di tabel AKUN
                cursor.execute(query_akun)
                akun_result = cursor.fetchone()
                if akun_result:
                    email_found = akun_result[0]
                    roles.add('akun')

                    # Cek di tabel ARTIST
                    cursor.execute(query_artist)
                    artist_result = cursor.fetchone()
                    if artist_result:
                        roles.add('artist')

                    # Cek di tabel SONGWRITER
                    cursor.execute(query_songwriter)
                    songwriter_result = cursor.fetchone()
                    if songwriter_result:
                        roles.add('songwriter')

                    # Cek di tabel PODCASTER
                    cursor.execute(query_podcaster)
                    podcaster_result = cursor.fetchone()
                    print("podcaster",podcaster_result)
                    if podcaster_result:
                        roles.add('podcaster')

                # Jika tidak ditemukan di tabel AKUN, cek di tabel LABEL
                if not roles:
                    cursor.execute(query_label)
                    label_result = cursor.fetchone()
                    if label_result:
                        email_found = label_result[0]
                        roles.add(label_result[1])

                if roles:
                    request.session['email'] = email_found
                    request.session['roles'] = ', '.join(roles)
                    print(roles)
                    return redirect('main:show_dashboard')
                else:
                    messages.error(request, 'Email atau password salah')

        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')

    return render(request, 'login.html')

def registrasi(request):
    return render(request, 'register.html')

@csrf_exempt
def registrasi_pengguna(request):
    cursor = connection.cursor()

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('name')
        gender = request.POST.get('gender')
        tempat_lahir = request.POST.get('tempat_lahir')
        tanggal_lahir = request.POST.get('tanggal_lahir')
        kota_asal = request.POST.get('kota_asal')
        roles = request.POST.getlist('roles')

        if not (email and password and nama and gender and tempat_lahir and tanggal_lahir and kota_asal):
            return render(request, 'registerpengguna.html', {'messages':['Semua field harus diisi']})
        
        try:
            # Tentukan nilai is_verified
            is_verified = bool(roles)

            if gender == 'L':
                gender = 0
            else:
                gender = 1

            # Insert ke tabel AKUN
            cursor.execute("""
                INSERT INTO AKUN (email, password, nama, gender, tempat_lahir, tanggal_lahir, kota_asal, is_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [email, password, nama, gender, tempat_lahir, tanggal_lahir, kota_asal, is_verified])

            # Insert ke tabel PEMILIK_HAK_CIPTA jika role adalah artist atau songwriter
            pemilik_hak_cipta_id = None
            if 'artist' in roles or 'songwriter' in roles:
                pemilik_hak_cipta_id = uuid4()
                rate_royalti = random.randint(20, 100)
                cursor.execute("""
                    INSERT INTO PEMILIK_HAK_CIPTA (id, rate_royalti)
                    VALUES (%s, %s)
                """, [pemilik_hak_cipta_id, rate_royalti])

            # Insert ke tabel ARTIST
            if 'artist' in roles:
                artist_id = uuid4()
                cursor.execute("""
                    INSERT INTO ARTIST (id, email_akun, id_pemilik_hak_cipta)
                    VALUES (%s, %s, %s)
                """, [artist_id, email, pemilik_hak_cipta_id])

            # Insert ke tabel SONGWRITER
            if 'songwriter' in roles:
                songwriter_id = uuid4()
                cursor.execute("""
                    INSERT INTO SONGWRITER (id, email_akun, id_pemilik_hak_cipta)
                    VALUES (%s, %s, %s)
                """, [songwriter_id, email, pemilik_hak_cipta_id])

            # Insert ke tabel PODCASTER
            if 'podcaster' in roles:
                cursor.execute("""
                    INSERT INTO PODCASTER (email)
                    VALUES (%s)
                """, [email])

            return redirect('authentication:login_view')

        except Exception as e:
            return render(request, 'registerpengguna.html', {'messages': [str(e)]})
        
    return render(request, 'registerpengguna.html')

@csrf_exempt
def registrasi_label(request):
    cursor = connection.cursor()

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        kontak = request.POST.get('kontak')

        if not (email and password and nama and kontak):
            return render(request, 'registerlabel.html', {'messages':['Semua field harus diisi']})

        try:
            # insert ke tabel pemilik hak cipta
            pemilik_hak_cipta_id = uuid4()
            rate_royalti = random.randint(20, 100)
            cursor.execute("""
                INSERT INTO PEMILIK_HAK_CIPTA (id, rate_royalti)
                VALUES (%s, %s)
            """, [pemilik_hak_cipta_id, rate_royalti])

            # insert ke tabel label
            id_label = uuid4()
            cursor.execute("""
                INSERT INTO LABEL (id, nama, email, password, kontak, id_pemilik_hak_cipta)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [id_label, nama, email, password, kontak, pemilik_hak_cipta_id])

            return redirect('authentication:login_view')
        
        except Exception as e:
            return render(request, 'registerlabel.html', {'messages': [str(e)]})

    return render(request, 'registerlabel.html')

def logout(request):
    request.session['email'] = 'not found'
    request.session['roles'] = 'not found'
    print("setelah logout")
    print(request.session['email'])
    print(request.session['roles'])
    response = HttpResponseRedirect(reverse('authentication:show_start'))
    return response