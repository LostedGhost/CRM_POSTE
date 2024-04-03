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
    date_creation = models.DateTimeField(auto_now_add=True)
    date_cessation = models.DateTimeField(default=timezone.datetime(9999, 12, 31))
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH, default="")
    
    
    def date_creation_rep(self):
        return self.date_creation.strftime("%Y-%m-%d %H:%M:%S") if self.date_creation != INFINITY_DATE else "Infinie"
    
    def date_cessation_rep(self):
        return self.date_cessation.strftime("%Y-%m-%d %H:%M:%S") if self.date_cessation != INFINITY_DATE else "Infinie"
    
        
    class Meta:
        abstract = True

class Profil(BaseEntity):
    """ id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
     """
    libelle = models.CharField(max_length=MAX_LABEL_LENGTH)
    
    def real_number():
        return Profil.objects.all().values_list('code', flat=True).distinct().count()

class Ville(BaseEntity):
    """ id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False) """

    intitule = models.CharField(max_length=MAX_LABEL_LENGTH)

class Agence(BaseEntity):
    """ id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False) """
    
    intitule = models.CharField(max_length=MAX_LABEL_LENGTH)
    site = models.CharField(max_length=MAX_LABEL_LENGTH)
    
    def sollicitation(self):
        services = Service.objects.filter(date_cessation=INFINITY_DATE)
        sol = [s.sollicitation_agence_by_code(self.code) for s in services]
        return sol
    
    def real_number():
        return Agence.objects.all().values_list('code', flat=True).distinct().count()

class Utilisateur(BaseEntity):
    """ id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False) """
    
    nom = models.CharField(max_length=MAX_LABEL_LENGTH)
    prenom = models.CharField(max_length=MAX_LABEL_LENGTH)
    email = models.EmailField()
    telephone = models.CharField(max_length=10)
    adresse = models.CharField(max_length=MAX_LABEL_LENGTH)
    login = models.CharField(max_length=MAX_LABEL_LENGTH)
    password = models.CharField(max_length=MAX_LABEL_LENGTH)
    photo = models.ImageField(upload_to="photos/profil", blank=True)
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="profil_utilisateur")
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name="agence_utilisateur", null=True)
    is_active = models.BooleanField(default=False)
    can_connect = models.BooleanField(default=True)
    
    def nom_prenom(self):
        return f"{self.nom} {self.prenom}"
    
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
    
    def sollicitation(self):
        services = Service.objects.filter(date_cessation=INFINITY_DATE)
        sol = [s.sollicitation_agent_by_code(self.code) for s in services]
        return sol
    
    def sollicitation_agence(self):
        services = Service.objects.filter(date_cessation=INFINITY_DATE)
        sol = [s.sollicitation_agence_by_code(self.agence.code) for s in services]
        return sol
    
    def real_number():
        return Utilisateur.objects.all().values_list('code', flat=True).distinct().count()
    
class AddUsersFiles(models.Model):
    fichier_xl = models.FileField(upload_to="excel_files", null=True)

class Entite(BaseEntity):
    """ id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False) """
    
    denomination = models.CharField(max_length=MAX_LABEL_LENGTH)
    def real_number():
        return Entite.objects.all().values_list('code', flat=True).distinct().count()

class Structure(BaseEntity):
    """ id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False) """
    
    denomination = models.CharField(max_length=MAX_LABEL_LENGTH)
    entite = models.ForeignKey(Entite, on_delete=models.CASCADE, related_name="entite_structure", null=True)

    def real_number():
        return Structure.objects.all().values_list('code', flat=True).distinct().count()
class Service(BaseEntity):
    """ id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False) """
    
    intitule = models.CharField(max_length=MAX_LABEL_LENGTH)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name="structure_service")
    montant = models.FloatField(default=0)
    couleur = models.CharField(max_length=MAX_LABEL_LENGTH, default='#fff')
    delai = models.IntegerField(default=0)
    
    
    def generate_color():
        color = generer_code_couleur()
        while color in Service.objects.filter(date_cessation=INFINITY_DATE).values_list('couleur', flat=True).distinct():
            color = generer_code_couleur()
        return color

    def sollicitation(self):
        s = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(service=self)
        return s
    
    def sollicitation_count(self):
        return Demande.objects.filter(date_cessation=INFINITY_DATE).filter(service=self).count()
    
    def sollicitation_agence_by_code(self, agence_code):
        s = 0
        for d in Demande.objects.filter(date_cessation=INFINITY_DATE).filter(service=self):
            if d.agent.agence.code == agence_code:
                s += 1
        return s
    
    def sollicitation_agent_by_code(self, agent_code):
        s = 0
        for d in Demande.objects.filter(date_cessation=INFINITY_DATE).filter(service=self):
            if d.agent.code == agent_code:
                s += 1
        return s
    
    def sollicitation_by_period(self, date_debut, date_fin):
        s = 0
        for d in Demande.objects.filter(date_cessation=INFINITY_DATE).filter(service=self).filter(date_creation__range=(date_debut, date_fin)):
            s += 1
        return s
    
    def solliciation_by_agence_and_period(self, agence_code, date_debut, date_fin):
        s = 0
        for d in Demande.objects.filter(date_cessation=INFINITY_DATE).filter(service=self).filter(agent__agence__code=agence_code).filter(date_creation__range=(date_debut, date_fin)):
            s += 1
        return s
    
    def real_number():
        return Service.objects.all().values_list('code', flat=True).distinct().count()

class Client(BaseEntity):
    """ id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False) """
    
    nom = models.CharField(max_length=MAX_LABEL_LENGTH)
    prenom = models.CharField(max_length=MAX_LABEL_LENGTH)
    date_naissance = models.DateField(default=BIRTH_DEFAULT)
    telephone = models.CharField(max_length=MAX_LABEL_LENGTH)
    email = models.EmailField(max_length=MAX_LABEL_LENGTH)
    adresse = models.CharField(max_length=MAX_LABEL_LENGTH)
    
    def real_number():
        return Client.objects.all().values_list('code', flat=True).distinct().count()
    def date_naissance_rep(self):
        birthdate=""
        birthdate+=str(self.date_naissance.year)+"-"+'{:02d}'.format(self.date_naissance.month)+"-"+'{:02d}'.format(self.date_naissance.day)
        return birthdate
    
    def nom_prenom(self):
        return f"{self.nom} {self.prenom}"
    
    

class StatutDemande(BaseEntity):
    """ id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False) """
    
    libelle = models.CharField(max_length=MAX_LABEL_LENGTH)
    def real_number():
        return StatutDemande.objects.all().values_list('code', flat=True).distinct().count()

class Demande(BaseEntity):
    """ id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False) """
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client_demande")
    agent = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="agent_demande")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="service_demande")
    statut = models.ForeignKey(StatutDemande, on_delete=models.CASCADE, related_name="statut_demande")
    observations = models.TextField(default="RAS")
    is_deleted = models.BooleanField(default=False)
    
    def date_butoire(self):
        return ajouter_jours(self.date_creation, self.service.delai)
    
    def optionsSupplementaires(self):
        return OptionSupplementaireDemande.objects.filter(demande=self)
    
    def optionsSupplementaires_today(self):
        return OptionSupplementaireDemande.objects.filter(demande=self).filter(date_creation__gt=premiere_heure_jour(), date_creation__lt=derniere_heure_jour())
    
    def montant_percu_today(self):
        optSup = self.optionsSupplementaires_today()
        montant = 0
        for op in optSup:
            montant += op.montantOpt()
        return montant
    
    
    def montant_percu(self):
        optSup = self.optionsSupplementaires()
        montant = 0
        for op in optSup:
            montant += op.montantOpt()
        return montant
    
    def optionSup(self, option):
        return OptionSupplementaireDemande.objects.get(demande=self, libelle=option)
    
    def tous_cout_supp(self):
        return OptionSupplementaireDemande.objects.filter(demande__code=self.code)
    
    def toutes_observations(self):
        all = Demande.objects.filter(code=self.code).values_list('observations', flat=True)
        return all
    
    def all_of_code(self):
        return Demande.objects.filter(code=self.code).order_by('id')
    def montant_total(self):
        opt = self.tous_cout_supp()
        montant = 0
        for o in opt:
            montant += o.montantOpt()
        return montant
    
    def real_number():
        return Demande.objects.all().values_list('code', flat=True).distinct().count()
    
    def to_dict(self):
        d = {}
        d['code'] = self.code
        d['date_creation'] = self.date_creation
        d['date_cessation'] = self.date_cessation
        d['modifier_par'] = self.modifier_par
        d['client_nom_prenom'] = self.client.nom + " " + self.client.prenom
        d['client_adresse'] = self.client.adresse
        d['client_email'] = self.client.email
        d['agence_nom'] = self.agent.agence.intitule
        d['agence_site'] = self.agent.agence.site
        d['agent_nom_prenom'] = self.agent.nom + " " + self.agent.prenom
        
        d['service'] = self.service.intitule
        d['opts'] = [{'libelle': o.option_supplementaire.libelle,'montant': o.option_supplementaire.montant, 'nombre':o.nombre, 'montantOpt':o.montantOpt()} for o in self.optionsSupplementaires()]
        d['opts_length'] = len(d['opts'])
        d['montant_percu'] = self.montant_percu()
        print(d)
        return d
    
    
class OptionSupplementaire(BaseEntity):
    """ id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False) """

    libelle = models.CharField(max_length=MAX_LABEL_LENGTH)
    montant = models.IntegerField(default=0)
    
    def libelle_rep(self):
        if self.libelle[0].lower() in "aeuiohy":
            return f"Nombre d'{self.libelle.lower()} éffectués(es)"
        else:
            return f"Nombre de {self.libelle.lower()} éffectués(es)"
    
    def real_number():
        return OptionSupplementaire.objects.all().values_list('code', flat=True).distinct().count()

class OptionSupplementaireDemande(BaseEntity):
    """ id = models.AutoField(primary_key=True, auto_created=True)
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    date_creation = models.DateField(auto_now_add=True)
    date_cessation = models.DateField(default=INFINITY_DATE)
    modifier_par = models.CharField(max_length=MAX_CODE_LENGTH)
    is_deleted = models.BooleanField(default=False) """
    
    demande = models.ForeignKey(Demande, on_delete=models.CASCADE, related_name="demande_option_supplementaire")
    option_supplementaire = models.ForeignKey(OptionSupplementaire, on_delete=models.CASCADE, related_name="option_supplementaire_demande")
    nombre = models.IntegerField(default=0)
    
    def montantOpt(self):
        return self.option_supplementaire.montant * self.nombre
    
    def real_number():
        return OptionSupplementaireDemande.objects.all().values_list('code', flat=True).distinct().count()

class Validation(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    day = models.DateTimeField(auto_now_add=True)
    validate = models.BooleanField(default=False)
    validator = models.ForeignKey(Utilisateur, related_name='validators',on_delete=models.CASCADE, default=None)
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, default=None)
    montant = models.IntegerField(null=True)
    
    def montant_validation(self):
        pass

class ValidationDemande(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    validation = models.ForeignKey(Validation, related_name='validations', on_delete=models.CASCADE, default=None)
    demande = models.ForeignKey(Demande, on_delete=models.CASCADE, default=None)