from django.shortcuts import render
from django.shortcuts import redirect
import openpyxl
from CRM.settings import BASE_DIR
from .models import *

# Create your views here.

def index(request):
    user_identifiant = request.session.get('user')
    error = request.session.get('error')
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.get(id=user_identifiant)
    nb_agents = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(profil__libelle="AGENT").count()
    nb_agents_active = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(profil__libelle="AGENT").filter(is_active=True).count()
    nb_demandes = Demande.objects.filter(date_cessation=INFINITY_DATE).count()
    nb_demandes_abouties = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(statut=StatutDemande.objects.filter(date_cessation=INFINITY_DATE).get(libelle="ABOUTIE")).count()
    return render(request, 'index.html', 
                  {"utilisateur": user,
                   "error": error,
                   "nb_agents": nb_agents,
                   "nb_agents_active": nb_agents_active,
                   "nb_demandes":nb_demandes,
                   "nb_demandes_abouties":nb_demandes_abouties,
                   }
                  )

def login(request):
    user_identifiant = request.session.get('user')
    error = request.session.get('error')
    if user_identifiant is not None:
        return redirect("/")
    if request.POST:
        login = request.POST['login']
        password = request.POST['password']
        try:
            user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(login=login, password=chiffrement_cesar(password, SECRET))
        except:
            request.session['error'] = 'Login ou mot de passe incorrect'
        request.session['user'] = user.id
        user.is_active = True
        user.save()
        return redirect("/")
    return render(request, 'login.html', {'error': error})

def logout(request):
    user_identifiant = request.session.get('user')
    if user_identifiant is not None:
        user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
        user.is_active = False
        user.save()
    request.session.clear()
    return redirect("/login")

def profile(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    if request.POST:
        nom = request.POST.get('nom').upper()
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse')
        date_naissance = request.POST.get('date_naissance')
        photo = request.FILES.get('photo')
        if photo == None:
            photo = user.photo
        password = request.POST.get('password')
        
        u = Utilisateur(photo=photo, code=user.code,nom=nom, prenom=prenom, agence=user.agence, date_naissance=date_naissance, telephone=telephone, email=email, adresse=adresse, login=user.login, password=chiffrement_cesar(password, SECRET), profil=user.profil,modifier_par=user.code)
        u.save()
        
        user.date_cessation = datetime.now()
        user.modifier_par = user.code
        user.save()
        request.session["user"] = u.id
        return redirect("/profil")
    return render(request, 'agents/profil.html',
                  {"utilisateur": user,
                   "error": error,
                   }
                  )

def liste_agent(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    agents = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(profil=Profil.objects.get(id=2))
    return render(request, 'agents/list.html',
                  {"utilisateur": user,
                   "error":error,
                   "agents": agents,
                   }
                  )

def ajout_agent(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    max_date = datetime.now() - timedelta(days=18*365)
    agences = Agence.objects.filter(date_cessation=INFINITY_DATE)
    if request.POST:
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        date_naissance = request.POST['date_naissance']
        email = request.POST['email']
        telephone = request.POST['telephone']
        adresse = request.POST['adresse']
        agence = Agence.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST['agence'])
        profil = Profil.objects.get(libelle="AGENT")
        login = Utilisateur.generate_login()
        password = Utilisateur.generate_password()
        code = generate_code("UTL", Utilisateur.objects.count()+1)
        modifier_par = user.code
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(nom=nom, prenom=prenom, date_naissance=date_naissance)
            request.session['error'] = 'Un utilisateur ayant le même nom, le même prénom et la même date de naissance existe déjà.'
            return redirect("/agents/list")
        except:
            pass
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(email=email)
            request.session['error'] = 'Email déjà utilisé'
            return redirect("/agents/list")
        except:
            pass
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(telephone=telephone)
            request.session['error'] = 'Telephone déjà utilisé'
            return redirect("/agents/list")
        except:
            pass
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(date_naissance__gt=max_date)
            request.session['error'] = 'Date invalide'
            return redirect("/agents/list")
        except:
            pass
        u = Utilisateur(code=code,nom=nom, prenom=prenom, agence=agence, date_naissance=date_naissance, telephone=telephone, email=email, adresse=adresse, login=login, password=chiffrement_cesar(password, SECRET), profil=profil,modifier_par=modifier_par)
        u.save()
        return redirect("/agents/list")
    return render(request, 'agents/add.html',{
        "utilisateur": user,
        "error": error,
        "max_date":max_date.strftime("%Y-%m-%d"),
        "agences":agences,
    })
    
def reaffectation_agent(request, agent_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    agences = Agence.objects.filter(date_cessation=INFINITY_DATE)
    agent = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=agent_id)
    password = dechiffrement_cesar(agent.password, SECRET)
    if request.POST:
        login = request.POST['login']
        password = request.POST['password']
        agence = Agence.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST['agence'])
        modifier_par = user.code
        profil = Profil.objects.get(libelle="AGENT")
        u = Utilisateur(code=agent.code,nom=agent.nom, prenom=agent.prenom, agence=agence, date_naissance=agent.date_naissance, telephone=agent.telephone, email=agent.email, adresse=agent.adresse, login=login, password=chiffrement_cesar(password, SECRET), profil=profil,modifier_par=modifier_par)
        u.save()
        agent.date_cessation = datetime.now()
        agent.modifier_par = user.code
        agent.save()
        return redirect("/agents/list")
    return render(request, 'agents/reaffectation.html',{
        "utilisateur": user,
        "error":error,
        "agences": agences,
        "agent": agent,
        "password":password,
    }
    )

def add_many_agents(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    if request.POST:
        usersFile = request.FILES["usersFile"]
        usersFile = AddUsersFiles(fichier_xl=usersFile)
        usersFile.save()
        classeur = openpyxl.load_workbook(str(BASE_DIR) + usersFile.fichier_xl.url)
        feuille = classeur.active
        donnees = []
        for row in feuille.iter_rows(values_only=True):
            ligne = []
            for cell in row:
                ligne.append(cell)
            donnees.append(ligne)
        donnees.pop(0)
    return render(request, 'agents/add_many.html',
                  {
                      "utilisateur": user,
                      "error":error,
                  })

def liste_agences(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    agences = Agence.objects.filter(date_cessation=INFINITY_DATE)
    return render(request, 'agence/list.html',
                  {"utilisateur": user,
                   "error": error,
                   "agences": agences,
                   }
    )
def ajout_agence(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    villes = Ville.objects.filter(date_cessation=INFINITY_DATE)
    if request.POST:
        intitule = request.POST["intitule"].upper()
        site = request.POST["site"].upper()
        longitude = None
        latitude = None
        try:
            lo = request.POST["geolocalisation_longitude"]
            lo = lo.replace(",", ".")
            la = request.POST["geolocalisation_latitude"]
            la = la.replace(",", ".")
            longitude = float(lo)
            latitude = float(la)
        except:
            request.session['error '] = 'L\'une des données de géolocalisation est incorrecte.'
            return redirect("/agence/add")
        
        try:
            Agence.objects.filter(date_cessation=INFINITY_DATE).get(intitule=intitule)
            request.session['error'] = 'L\'agence existe déjà.'
            return redirect("/agence/add")
        except:
            pass
        try:
            Agence.objects.filter(date_cessation=INFINITY_DATE).get(longitude=longitude, latitude=latitude)
            request.session['error'] = 'L\'agence existe déjà.'
            return redirect("/agence/add")
        except:
            pass
        try:
            Agence.objects.filter(date_cessation=INFINITY_DATE).get(intitule=intitule,site=site)
            request.session['error'] = 'L\'agence existe déjà.'
            return redirect("/agence/add")
        except:
            pass
        code = generate_code("AGC", Agence.objects.filter(date_cessation=INFINITY_DATE).count()+1)
        modifier_par = user.code
        agence = Agence(code = code, modifier_par =modifier_par ,site=site, intitule=intitule, geolocalisation_longitude=longitude, geolocalisation_latitude=latitude)
        agence.save()
        return redirect("/agence/list")
    return render(request, 'agence/add.html',
                  {"utilisateur": user,
                   "error":error,
                   "villes": villes,
                   }
    )

def edit_agence(request, agence_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    agence = Agence.objects.filter(date_cessation=INFINITY_DATE).get(id=agence_id)
    villes = Ville.objects.filter(date_cessation=INFINITY_DATE)
    agences = Agence.objects.filter(date_cessation=INFINITY_DATE)
    if request.POST:
        intitule = request.POST["intitule"].upper()
        site = request.POST["site"].upper()
        longitude = None
        latitude = None
        agence.date_cessation = datetime.now()
        agence.modifier_par = user.code
        agence.save()
        try:
            lo = request.POST["geolocalisation_longitude"]
            lo = lo.replace(",", ".")
            la = request.POST["geolocalisation_latitude"]
            la = la.replace(",", ".")
            longitude = float(lo)
            latitude = float(la)
        except:
            request.session['error'] = 'L\'une des données de géolocalisation est incorrecte.'
            agence.date_cessation = INFINITY_DATE
            agence.save()
            return redirect("/agence/list")
        
        try:
            Agence.objects.filter(date_cessation=INFINITY_DATE).get(intitule=intitule)
            request.session['error'] = 'L\'agence existe déjà.'
            agence.date_cessation = INFINITY_DATE
            agence.save()
            return redirect("/agence/list")
        except:
            pass
        try:
            Agence.objects.filter(date_cessation=INFINITY_DATE).get(longitude=longitude, latitude=latitude)
            request.session['error'] = 'L\'agence existe déjà.'
            agence.date_cessation = INFINITY_DATE
            agence.save()
            return redirect("/agence/list")
        except:
            pass
        try:
            Agence.objects.filter(date_cessation=INFINITY_DATE).get(intitule=intitule,site=site)
            request.session['error'] = 'L\'agence existe déjà.'
            agence.date_cessation = INFINITY_DATE
            agence.save()
            return redirect("/agence/list")
        except:
            pass
        modifier_par = user.code
        new_agence = Agence(code = agence.code, modifier_par =modifier_par ,site=site, intitule=intitule, geolocalisation_longitude=longitude, geolocalisation_latitude=latitude)
        new_agence.save()
        return redirect("/agence/list")
    return render(request, 'agence/edit.html',
                  {
                      "utilisateur": user,
                      "error":error,
                      "agence":agence,
                      "villes": villes,
                  })

def delete_agence(request, agence_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    agence = Agence.objects.filter(date_cessation=INFINITY_DATE).get(id=agence_id)
    agents = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(agence=agence)
    for agent in agents:
        agent.date_cessation = datetime.now()
        agent.modifier_par = user.code
        agent.save()
    agence.date_cessation = datetime.now()
    agence.modifier_par = user.code
    agence.save()
    return redirect("/agence/list")

def liste_entite(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    entites = Entite.objects.filter(date_cessation=INFINITY_DATE)
    return render(request, 'entite/list.html',
                  {"utilisateur": user,
                   "error": error,
                   "entites":entites,
                  }
    )

def ajout_entite(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    if request.POST:
        denomination = request.POST.get('denomination').upper()
        code = code = generate_code("ENT", Entite.objects.count()+1)
        try:
            Entite.objects.filter(date_cessation=INFINITY_DATE).get(denomination=denomination)
            request.session['error'] = 'L\'entité existe déjà.'
            return redirect("/entite/list")
        except:
            pass
        entite = Entite(code=code, denomination=denomination, modifier_par=user.code)
        entite.save()
        return redirect("/entite/list")
    return render(request, 'entite/add.html',
                  {"utilisateur": user,
                   "error": error,
                  }
    )

def modifier_entite(request, entite_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    entite = Entite.objects.filter(date_cessation=INFINITY_DATE).get(id=entite_id)
    if request.POST:
        denomination = request.POST.get('denomination').upper()
        entite.date_cessation = datetime.now()
        entite.modifier_par = user.code
        entite.save()
        try:
            Entite.objects.filter(date_cessation=INFINITY_DATE).get(denomination=denomination)
            request.session['error'] = 'L\'entité existe déjà.'
            entite.date_cessation = INFINITY_DATE
            entite.save()
            return redirect("/entite/list")
        except:
            pass
        
        new_entite = Entite(code=entite.code, denomination=denomination, modifier_par=user.code)
        new_entite.save()
        return redirect("/entite/list")
    return render(request, 'entite/edit.html',
                  {"utilisateur": user,
                   "error": error,
                   "entite": entite,
                  }
    )

def delete_entite(request, entite_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    entite = Entite.objects.filter(date_cessation=INFINITY_DATE).get(id=entite_id)
    entite.date_cessation = datetime.now()
    entite.modifier_par = user.code
    entite.save()
    return redirect("/entite/list")

def liste_structure(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    structures = Structure.objects.filter(date_cessation=INFINITY_DATE)
    return render(request,'structure/list.html',
                  {"utilisateur": user,
                   "error": error,
                   "structures":structures,
                  }
    )

def ajout_structure(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    entites = Entite.objects.filter(date_cessation=INFINITY_DATE)
    if request.POST:
        denomination = request.POST.get('denomination').upper()
        entite=  Entite.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST.get('entite'))
        code = code = generate_code("STR", Structure.objects.count()+1)
        try:
            Structure.objects.filter(date_cessation=INFINITY_DATE).get(denomination=denomination)
            request.session['error'] = 'La structure existe déjà.'
            return redirect("/structure/list")
        except:
            pass
        structure = Structure(code=code, denomination=denomination, modifier_par=user.code, entite=entite)
        structure.save()
        return redirect("/structure/list")
    return render(request,'structure/add.html',
                  {"utilisateur": user,
                   "error": error,
                   "entites":entites,
                  }
    )

def edit_structure(request, struc_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    entites = Entite.objects.filter(date_cessation=INFINITY_DATE)
    structure = Structure.objects.filter(date_cessation=INFINITY_DATE).get(id=struc_id)
    if request.POST:
        denomination = request.POST.get('denomination').upper()
        entite=  Entite.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST.get('entite'))
        structure.date_cessation = datetime.now()
        structure.modifier_par = user.code
        structure.save()
        try:
            Structure.objects.filter(date_cessation=INFINITY_DATE).get(denomination=denomination)
            request.session['error'] = 'La structure existe déjà.'
            structure.date_cessation = INFINITY_DATE
            structure.save()
            return redirect("/structure/list")
        except:
            pass
        
        new_struc = Structure(code=structure.code, denomination=denomination, modifier_par=user.code, entite=entite)
        new_struc.save()
        return redirect("/structure/list")
    return render(request,'structure/edit.html',
                  {"utilisateur": user,
                   "error": error,
                   "entites":entites,
                   "structure":structure,
                  }
    )
    
def delete_structure(request, struc_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    structure = Structure.objects.filter(date_cessation=INFINITY_DATE).get(id=struc_id)
    structure.date_cessation = datetime.now()
    structure.modifier_par = user.code
    structure.save()
    return redirect("/structure/list")

def liste_services(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    services = Service.objects.filter(date_cessation=INFINITY_DATE)
    return render(request,'service/list.html',
                  {"utilisateur": user,
                   "error": error,
                   "services":services,
                  }
    )

def ajout_service(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    structures = Structure.objects.filter(date_cessation=INFINITY_DATE).order_by('entite')
    if request.POST:
        intitule = request.POST.get('intitule', None)
        structure = request.POST.get('structure')
        structure = Structure.objects.filter(date_cessation=INFINITY_DATE).get(code=structure)
        photo = request.FILES['photo']
        montant = request.POST.get('montant', None)
        
        try:
            montant = float(montant)
        except:
            request.session['error'] = 'Le montant doit être un nombre.'
            return redirect("/service/list")
        try:
            Service.objects.filter(date_cessation=INFINITY_DATE).get(intitule=intitule)
            request.session['error'] = 'Le service existe déjà.'
        except:
            code = code = generate_code("SRV", Service.objects.count()+1)
            service = Service(code=code, intitule=intitule, montant=montant, modifier_par=user.code, structure=structure, photo=photo)
            service.save()
        
        return redirect("/service/list")
    return render(request,'service/add.html',
                  {"utilisateur": user,
                   "error": error,
                   "structures":structures,
                  }
    )

def edit_service(request, serv_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    structures = Structure.objects.filter(date_cessation=INFINITY_DATE).order_by('entite')
    service = Service.objects.filter(date_cessation=INFINITY_DATE).get(id=serv_id)
    if request.POST:
        intitule = request.POST.get('intitule', None)
        structure = request.POST.get('structure')
        structure = Structure.objects.filter(date_cessation=INFINITY_DATE).get(code=structure)
        photo = request.FILES.get('photo', None)
        service.date_cessation = datetime.now()
        service.modifier_par = user.code
        service.save()
        try:
            Service.objects.filter(date_cessation=INFINITY_DATE).get(intitule=intitule)
            request.session['error'] = 'Le service existe déjà.'
            service.date_cessation = INFINITY_DATE
            service.save()
            return redirect("/service/list")
        except:
            pass
        new_service = Service(code=service.code, intitule=intitule, modifier_par=user.code, structure=structure)
        if photo is None:
            new_service.photo = service.photo
        else:
            new_service.photo = photo
        new_service.save()

        return redirect("/service/list")
    return render(request, 'service/edit.html',
                  {
                      "utilisateur": user,
                      "error": error,
                      "structures": structures,
                      "service": service,
                  })

def liste_option_sup(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    options = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE)
    return render(request, 'option/list.html',
                  {"utilisateur": user,
                   "error": error,
                   "options":options,
                  }
    )
def ajout_option(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    if request.POST:
        intitule = request.POST.get('intitule', None)
        montant = request.POST.get('montant', None)
        try:
            OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE).get(libelle=intitule)
            request.session['error'] = 'L\'option existe déjà.'
        except:
            code = code = generate_code("OPT", OptionSupplementaire.objects.count()+1)
            option = OptionSupplementaire(code=code, libelle=intitule, montant=montant, modifier_par=user.code)
            option.save()
        return redirect("/option/list")
    return render(request, 'option/add.html',
                  {"utilisateur": user,
                   "error": error,
                  }
    )
def edit_option(request, opt_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    option = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE).get(id=opt_id)
    if request.POST:
        intitule = request.POST.get('intitule', None)
        montant = request.POST.get('montant', None)
        option.date_cessation = datetime.now()
        option.modifier_par = user.code
        option.save()
        try:
            OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE).get(libelle=intitule)
            request.session['error'] = 'L\'option existe déjà.'
            option.date_cessation = INFINITY_DATE
            option.save()
            return redirect("/option/list")
        except:
            pass
        new_option = OptionSupplementaire(code=option.code, libelle=intitule, montant=montant, modifier_par=user.code)
        new_option.save()
        return redirect("/option/list")
    return render(request, 'option/edit.html',
                  {"utilisateur": user,
                   "error": error,
                   "option": option,
                  }
    )

def delete_option(request, opt_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    option = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE).get(id=opt_id)
    option.date_cessation = datetime.now()
    option.modifier_par = user.code
    option.save()
    return redirect("/option/list")

def liste_demande(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    demandes = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(agent=user).order_by('-id')
    options_sup = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE)
    return render(request, 'demande/list.html',
                  {"utilisateur": user,
                   "error": error,
                   "demandes":demandes,
                   "options_sup":options_sup,
                  }
    )

def ajout_demande(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    services = Service.objects.filter(date_cessation=INFINITY_DATE)
    clients = Client.objects.filter(date_cessation=INFINITY_DATE)
    options_sup = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE)
    if request.POST:
        if "nom" in request.POST:
            nom = request.POST["nom"]
            prenom = request.POST["prenom"]
            email = request.POST["email"]
            telephone = request.POST["telephone"]
            adresse = request.POST["adresse"]
            date_naissance = request.POST["date_naissance"]
            try:
                cl = Client.objects.filter(date_cessation=INFINITY_DATE).get(nom=nom, prenom=prenom, date_naissance=date_naissance, email=email)
                request.session["error"]=  f"Le client existe déjà et son code est {cl.code}"
                return redirect("/demande/add")
            except:
                pass
            
            try:
                cl = Client.objects.filter(date_cessation=INFINITY_DATE).get(telephone=telephone)
                request.session["error"]=  f"Le client existe déjà et son code est {cl.code}"
                return redirect("/demande/add")
            except:
                pass
            
            try:
                cl = Client.objects.filter(date_cessation=INFINITY_DATE).get(email=email)
                request.session["error"]=  f"Le client existe déjà et son code est {cl.code}"
                return redirect("/demande/add")
            except:
                pass
            service = Service.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST["service"])
            
            code = generate_code("DEM", Demande.objects.count()+1)
            code_client = generate_code("CLIENT",Client.objects.count()+1)
            statut = StatutDemande.objects.filter(date_cessation=INFINITY_DATE).get(libelle="INITIE")
            client = Client(code=code_client, modifier_par=user.code, nom=nom, prenom=prenom, date_naissance=date_naissance, telephone=telephone, email=email, adresse=adresse)
            client.save()
            demande = Demande(statut= statut, client=client,code=code, modifier_par=user.code, agent=Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(code=user.code), service=service, observations=str(request.POST.get('observations', None)))
            demande.save()
            
            nb_options_names = [f"nb{op.id}" for op in options_sup]
            for opt in nb_options_names:
                if opt in request.POST:
                    nb = request.POST[opt]
                    if nb != "":
                        nb = int(nb)
                    else:
                        nb = 0
                    code = generate_code("OPTDEM", OptionSupplementaireDemande.objects.count()+1)
                    option = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE).get(id=int(opt.replace("nb", "")))
                    optionSupDemand = OptionSupplementaireDemande(demande=demande, option_supplementaire=option, nombre=nb, code=code, modifier_par=user.code)
                    optionSupDemand.save()
        else:
            client = Client.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST["client"])
            service = Service.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST["service"])
            
            code = generate_code("DEM", Demande.objects.count()+1)
            statut = StatutDemande.objects.filter(date_cessation=INFINITY_DATE).get(libelle="INITIE")
            demande = Demande(statut= statut, client=client,code=code, modifier_par=user.code, agent=Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(code=user.code), service=service, observations=str(request.POST.get('observations', None)))
            demande.save()
            
            nb_options_names = [f"nb{op.id}" for op in options_sup]
            for opt in nb_options_names:
                if opt in request.POST:
                    nb = request.POST[opt]
                    if nb != "":
                        nb = int(nb)
                    else:
                        nb = 0
                    code = generate_code("OPTDEM", OptionSupplementaireDemande.objects.count()+1)
                    option = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE).get(id=int(opt.replace("nb", "")))
                    optionSupDemand = OptionSupplementaireDemande(demande=demande, option_supplementaire=option, nombre=nb, code=code, modifier_par=user.code)
                    optionSupDemand.save()
        return redirect("/demande/list")
    return render(request, 'demande/add.html',
                  {"utilisateur": user,
                   "error": error,
                   "services":services,
                   "clients":clients,
                   "options_sup":options_sup,
                  }
    )

def suivre_demande(request,dem_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    demande = Demande.objects.filter(date_cessation=INFINITY_DATE).get(id=dem_id)
    options_sup = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE)
    statuts = StatutDemande.objects.filter(date_cessation=INFINITY_DATE)
    if request.POST:
        statut = request.POST.get('statut', None)
        observations = request.POST.get('observations', None)
        try:
            statut = StatutDemande.objects.filter(date_cessation=INFINITY_DATE).get(id=int(statut))
        except:
            statut = StatutDemande.objects.filter(date_cessation=INFINITY_DATE).get(id=5)
        new_demande = Demande(statut= statut, client=demande.client,code=demande.code, modifier_par=user.code, agent=Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(code=user.code), service=demande.service, observations=str(observations))
        new_demande.save()
        demande.date_cessation= datetime.now()
        demande.save()
        nb_options_names = [f"nb{op.id}" for op in options_sup]
        for opt in nb_options_names:
                if opt in request.POST:
                    nb = request.POST[opt]
                    if nb != "":
                        nb = int(nb)
                    else:
                        nb = 0
                    code = generate_code("OPTDEM", OptionSupplementaireDemande.objects.count()+1)
                    option = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE).get(id=int(opt.replace("nb", "")))
                    optionSupDemand = OptionSupplementaireDemande(demande=new_demande, option_supplementaire=option, nombre=nb, code=code, modifier_par=user.code)
                    optionSupDemand.save()
        return redirect("/demande/list")
    return render(request, 'demande/suivre.html',
                  {"utilisateur": user,
                   "error": error,
                   "demande":demande,
                   "options_sup":options_sup,
                   "statuts":statuts,
                  }
    )

def other_demande(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    agences = Agence.objects.filter(date_cessation=INFINITY_DATE)
    clients = Client.objects.filter(date_cessation=INFINITY_DATE)
    if request.POST:
        if "code" in request.POST:
            code = request.POST.get('code', None)
            return redirect(f"/demande/view/{code}")
        elif "agence" in request.POST:
            agence = request.POST.get('agence', None)
            return redirect(f"/demande/view_agence/{agence}")
        elif "client" in request.POST:
            client = request.POST.get('client', None)
            return redirect(f"/demande/view_client/{client}")
        elif "date" in request.POST:
            date = request.POST.get('date', None)
            year = date.split("-")[0]
            month = date.split("-")[1]
            day = date.split("-")[2]
            return redirect(f"/demande/view_date/{year}/{month}/{day}")
    return render(request, 'demande/other.html',
                  {"utilisateur": user,
                   "error": error,
                   "agences":agences,
                   "clients":clients
                  }
    )
    
def view_demande_by_code(request, dem_code):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    try:
        demande = Demande.objects.filter(date_cessation=INFINITY_DATE).get(code=dem_code)
    except:
        demande = None
    return render(request, 'demande/view.html',
                  {
                      "utilisateur":user,
                      "error":error,
                      "demande":demande,
                  }
    )

def view_demande_by_agence(request, agence_code):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    try:
        agence = Agence.objects.filter(date_cessation=INFINITY_DATE).get(code=agence_code)
    except:
        agence = None
        demandes = None
    if agence is not None:
        agents = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(agence=agence)
        demandes = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(agent__in=agents)
    return render(request, 'demande/view_agence.html',
                  {
                      "utilisateur":user,
                      "error":error,
                      "demandes":demandes,
                  }
    )

def view_demande_by_client(request, client_code):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    try:
        client = Client.objects.filter(date_cessation=INFINITY_DATE).get(code=client_code)
    except:
        client = None
        demandes = None
    if client is not None:
        demandes = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(client=client)
    return render(request, 'demande/view_client.html',
                  {
                      "utilisateur":user,
                      "error":error,
                      "demandes":demandes,
                  }
    )

def view_demande_by_date(request, year, month, day):
    date = datetime(int(year), int(month), int(day))
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    try:
        demandes = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(date_creation=date)
    except:
        demandes = None
    return render(request, 'demande/view_date.html',
                  {
                      "utilisateur":user,
                      "error":error,
                      "demandes":demandes,
                  }
    )

def delete_demande(request, dem_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    demande = Demande.objects.filter(date_cessation=INFINITY_DATE).get(id=dem_id)
    demande.date_cessation = datetime.now()
    demande.modifier_par = user.code
    demande.save()
    return redirect("/demande/list")