from django.shortcuts import render

def show_albums(request):
    albums = [
        {'id':'6e09033e-54a9-418e-88fa-ab6229be116a', 'judul':'Dark Blood', 'jumlah_lagu':11, 'id_label':'6f649a4b-f64b-4cf6-843d-84f0bc96572e', 'total_durasi':37},
        {'id':'177a17b9-c1c9-4836-b3e6-4c52d456b2e1', 'judul':'Savage - The 1st Mini Album', 'jumlah_lagu':9, 'id_label':'b0aae604-6ce6-4fae-9b87-05c7e1ab735e', 'total_durasi':27},
        {'id':'c7eb8e04-bfd6-4ab0-83ec-607e0ba15e34', 'judul':'THE SECOND STEP : CHAPTER ONE', 'jumlah_lagu':8, 'id_label':'64763682-34b8-4765-bd64-9a8814c5522d', 'total_durasi':25},
        {'id':'2fdd6704-626e-45d2-8c6f-a461054bf5ab', 'judul':'5-STAR', 'jumlah_lagu':12, 'id_label':'7e9118cb-cbfb-4b95-94f8-4e07f5447bc9', 'total_durasi':48},
        {'id':'c71b5a88-c60f-43ba-ab8a-100691355095', 'judul':'I\'VE MINE', 'jumlah_lagu':10, 'id_label':'eff55dd5-4b88-4b85-b60b-c96461e247e9', 'total_durasi':33}
    ]

    context = {'albums':albums}

    return render(request, "list_albums.html", context)