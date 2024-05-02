from django.db import models
from django.contrib.auth.models import User

class Paket(models.Model):
    nama = models.CharField(max_length=100)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    durasi = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nama} - Rp{self.harga}"

class Transaksi(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaksi')
    paket = models.ForeignKey(Paket, on_delete=models.CASCADE)
    tanggal_mulai = models.DateTimeField(auto_now_add=True)
    metode_pembayaran = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.paket.nama}"
