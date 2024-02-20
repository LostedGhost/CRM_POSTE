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

class Ville(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False)

    intitule = models.CharField(max_length=MAX_LABEL_LENGTH)
    code_postal = models.CharField(max_length=MAX_LABEL_LENGTH)
    pays = models.CharField(max_length=MAX_LABEL_LENGTH)

class Agence(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False)
    
    intitule = models.CharField(max_length=MAX_LABEL_LENGTH)
    site = models.CharField(max_length=MAX_LABEL_LENGTH)
    geolocalisation_longitude = models.FloatField(default=0)
    geolocalisation_latitude = models.FloatField(default=0)

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
    photo = models.ImageField(upload_to="photos/profil", blank=True)
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
    
    def date_naissance_rep(self):
        birthdate=""
        birthdate+=str(self.date_naissance.year)+"-"+'{:02d}'.format(self.date_naissance.month)+"-"+'{:02d}'.format(self.date_naissance.day)
        return birthdate

    def true_pass(self):
        return dechiffrement_cesar(self.password, SECRET)
class AddUsersFiles(models.Model):
    fichier_xl = models.FileField(upload_to="excel_files", null=True)

class Entite(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False)
    
    denomination = models.CharField(max_length=MAX_LABEL_LENGTH)

class Structure(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False)
    
    denomination = models.CharField(max_length=MAX_LABEL_LENGTH)
    entite = models.ForeignKey(Entite, on_delete=models.CASCADE, related_name="entite_structure", null=True)

class Service(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False)
    
    intitule = models.CharField(max_length=MAX_LABEL_LENGTH)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name="structure_service")
    photo = models.ImageField(upload_to="photos/service", blank=True)
    montant = models.FloatField(default=0)
    nb_scannage = models.IntegerField(default=0)
    nb_impression = models.IntegerField(default=0)
    frais_supplementaire = models.FloatField(default=0)
    raisons_frais_sup = models.CharField(max_length=MAX_LABEL_LENGTH, default="")

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

class StatutDemande(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False)
    
    libelle = models.CharField(max_length=MAX_LABEL_LENGTH)

class Demande(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False)
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client_demande")
    agent = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="agent_demande")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="service_demande")