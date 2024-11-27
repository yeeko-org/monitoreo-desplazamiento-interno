from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=100, blank=True)
    full_editor = models.BooleanField(
        default=False, verbose_name='Es revisor',
        help_text='Puede editar cualquier contenido')
