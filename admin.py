from django.contrib import admin
from .models import UserProfile, NetworkScan

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date')  # Panelde hangi sütunlar görünsün
    search_fields = ('user__username', 'user__email')  # Arama kutusu neleri kapsasın
    list_filter = ('birth_date',)  # Sağda filtreleme imkânı

@admin.register(NetworkScan)
class NetworkScanAdmin(admin.ModelAdmin):
    list_display = ('user', 'target', 'interface', 'timestamp')  # Ana liste görünümü
    search_fields = ('user__username', 'target', 'interface')    # Aranabilir alanlar
    list_filter = ('timestamp',)                                 # Tarih filtresi
    readonly_fields = ('timestamp',)                             # Admin'de bu alan düzenlenemez
