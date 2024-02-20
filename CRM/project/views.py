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
    return render(request, 'index.html', 
                  {"utilisateur": user,
                   "error": error,
                   "nb_agents": nb_agents,
                   "nb_agents_active": nb_agents_active,
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
    agence = Agence.objects.filter(date_cessation=INFINITY_DATE).get(id=agence_id)
    agents = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(agence=agence)
    for agent in agents:
        agent.date_cessation = datetime.now()
        agent.save()
    agence.date_cessation = datetime.now()
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
    entite = Entite.objects.filter(date_cessation=INFINITY_DATE).get(id=entite_id)
    entite.date_cessation = datetime.now()
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
    structure = Structure.objects.filter(date_cessation=INFINITY_DATE).get(id=struc_id)
    structure.date_cessation = datetime.now()
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
        
        try:
            Service.objects.filter(date_cessation=INFINITY_DATE).get(intitule=intitule)
            request.session['error'] = 'Le service existe déjà.'
        except:
            code = code = generate_code("SRV", Service.objects.count()+1)
            service = Service(code=code, intitule=intitule, modifier_par=user.code, structure=structure, photo=photo)
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
    
def liste_demande(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    demandes = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(agent=user)
    return render(request, 'demande/list.html',
                  {"utilisateur": user,
                   "error": error,
                   "demandes":demandes,
                  }
    )

def ajout_demande(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    services = Service.objects.filter(date_cessation=INFINITY_DATE)
    return render(request, 'demande/add.html',
                  {"utilisateur": user,
                   "error": error,
                   "services":services,
                  }
    )