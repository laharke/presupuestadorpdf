from django.db import models
from django.contrib.auth.models import AbstractUser


#models

class User(AbstractUser):
    pass

class Dispositivo(models.Model):
    nombre = models.CharField(max_length=255, blank=False)
    precio = models.IntegerField()
    pagoUnico = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre
