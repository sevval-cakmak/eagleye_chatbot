
from django.db import models
from django.contrib.auth.models import User

# Kullanıcıya ait ek bilgiler (doğum tarihi gibi)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username


# Kullanıcının gerçekleştirdiği ağ taramaları
class NetworkScan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target = models.CharField(max_length=100)  # Örn: 192.168.1.0/24
    interface = models.CharField(max_length=50)  # Örn: wlan0, eth0
    scan_result = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.target} @ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
