from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login_view(request):
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