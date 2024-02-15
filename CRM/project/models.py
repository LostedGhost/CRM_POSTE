from django.db import models
from datetime import datetime

# FONCTIONS UTILES
from .utils import *

# VARIABLES GLOBALES
from .config import *

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
        
    class Meta:
        abstract = True

class Profil(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False)
    libelle = models.CharField(max_length=MAX_LABEL_LENGTH)

class Agence(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False)
    
    intitule = models.CharField(max_length=MAX_LABEL_LENGTH)
    site = models.CharField(max_length=MAX_LABEL_LENGTH)
    geolocalisation_longitude = models.IntegerField(default=0)
    geolocalisation_latitude = models.IntegerField(default=0)

class Utilisateur(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False)
    nom = models.CharField(max_length=MAX_LABEL_LENGTH)
    prenom = models.CharField(max_length=MAX_LABEL_LENGTH)
    date_naissance = models.DateField(default=BIRTH_DEFAULT)
    email = models.EmailField()
    telephone = models.CharField(max_length=10)
    adresse = models.CharField(max_length=MAX_LABEL_LENGTH)
    login = models.CharField(max_length=MAX_LABEL_LENGTH)
    password = models.CharField(max_length=MAX_LABEL_LENGTH)
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="profil_utilisateur")
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name="agence_utilisateur", null=True)
    is_active = models.BooleanField(default=False)
    
    def generate_login():
        c = generate_random("USER@")
        while True:
            try:
                Utilisateur.objects.get(login=c)
            except:
                return c
    
    def generate_password():
        return generate_code("PASS@", Utilisateur.objects.count())

class AddUsersFiles(models.Model):
    fichier_xl = models.FileField(upload_to="excel_files", null=True)

class Ticket(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False)
    

class Client(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False)
    
    nom = models.CharField(max_length=MAX_LABEL_LENGTH)
    prenom = models.CharField(max_length=MAX_LABEL_LENGTH)
    date_naissance = models.DateField(default=BIRTH_DEFAULT)
    telephone = models.CharField(max_length=MAX_LABEL_LENGTH)
    email = models.EmailField(max_length=MAX_LABEL_LENGTH)
    adresse = models.CharField(max_length=MAX_LABEL_LENGTH)