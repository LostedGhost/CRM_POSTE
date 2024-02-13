from django.db import models
from datetime import datetime
from utils import *

# VARIABLES GLOBALES

INFINITY_DATE = datetime(9999, 12, 31)
MAX_CODE_LENGTH = 10
MAX_LABEL_LENGTH = 100

# Create your models here.

class BaseEntity(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    
    def save(self, classe, prefix, *args, **kwargs):
        if not self.pk:
            self.code = generate_code(prefix, classe.objects.count())
        super(classe, self).save(*args, **kwargs)

class Profil(BaseEntity):
    libelle = models.CharField(max_length=MAX_LABEL_LENGTH)


class Utilisateur(BaseEntity):
    nom = models.CharField(max_length=MAX_LABEL_LENGTH)
    prenom = models.CharField(max_length=MAX_LABEL_LENGTH)
    email = models.EmailField()
    telephone = models.CharField(max_length=10)
    adresse = models.CharField(max_length=MAX_LABEL_LENGTH)
    login = models.CharField(max_length=MAX_LABEL_LENGTH)
    password = models.CharField(max_length=MAX_LABEL_LENGTH)