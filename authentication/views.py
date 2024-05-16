from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Query untuk memeriksa di tabel AKUN dan tabel terkait
        query_akun = f"""
        SELECT
            u.email,
            COALESCE(
                STRING_AGG(
                    DISTINCT
                    CASE
                        WHEN ar.email_akun IS NOT NULL THEN 'artist'
                        WHEN sw.email_akun IS NOT NULL THEN 'songwriter'
                        WHEN pc.email IS NOT NULL THEN 'podcaster'
                    END, ','
                ),
                'akun'
            ) AS roles
        FROM AKUN u
        LEFT JOIN ARTIST ar ON u.email = ar.email_akun
        LEFT JOIN SONGWRITER sw ON u.email = sw.email_akun
        LEFT JOIN PODCASTER pc ON u.email = pc.email
        WHERE u.email = '{email}' AND u.password = '{password}'
        GROUP BY u.email
        """

        # Query untuk memeriksa di tabel LABEL
        query_label = f"""
        SELECT
            l.email,
            'label' AS roles
        FROM LABEL l
        WHERE l.email = '{email}' AND l.password = '{password}'
        """

        try:
            with connection.cursor() as cursor:
                print("masukkkk sini")
                cursor.execute('SET search_path TO public')

                # Cek di tabel AKUN dan tabel terkait
                cursor.execute(query_akun)
                result = cursor.fetchone()
                print(result)

                if result:
                    request.session['email'] = result[0]
                    request.session['roles'] = result[1]
                    print("roles:", result[1])
                    return redirect('main:show_dashboard')
                else:
                    # Jika tidak ditemukan, cek di tabel LABEL
                    cursor.execute(query_label)
                    result = cursor.fetchone()
                    print(result)

                    if result:
                        request.session['email'] = result[0]
                        request.session['roles'] = result[1]
                        return redirect('main:show_dashboard')
                    else:
                        messages.error(request, 'Email atau password salah')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')

    return render(request, 'login.html')