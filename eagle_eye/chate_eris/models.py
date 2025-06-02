from django.db import models
from django.utils.text import slugify


# Create your models here.

class giris_mesaji(models.Model):
    metin=models.CharField(max_length=1000)
    slug=models.SlugField(max_length=155, unique=True,null=True,blank=True)

    def __str__(self):
        return self.metin
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.baslik)
        super().save(*args, **kwargs)

class gecmis(models.Model):
    gecmis_islemler=models.CharField(max_length=100)

    