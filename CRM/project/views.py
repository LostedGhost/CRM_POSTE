from django.shortcuts import render, redirect

import openpyxl
import csv
import io
import codecs
from django.http import HttpResponse
from CRM.settings import BASE_DIR
from .models import *




# Create your views here.
def handle404(request, exception):
    user_identifiant = request.session.get('user')
    error = request.session.get('error')
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.get(id=user_identifiant)
    return render(request, 'error/404.html', {'utilisateur': user, 'error': error})

def handle500(request):
    return render(request, 'error/500.html')

def index(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.get(id=user_identifiant)
    print(INFINITY_DATE)
    """ 
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(code=user.code)
    request.session['user'] = user.id """
    nb_agents = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(profil__libelle="AGENT").count()
    nb_agents_active = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(profil__id=2).filter(is_active=True).count()
    nb_demandes = Demande.objects.filter(date_cessation=INFINITY_DATE).count()
    nb_demandes_abouties = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(statut__id=5).count()
    nb_demandes_non_abouties = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(statut__id=4).count()
    nb_demandes_inities_ou_en_cours = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(statut__id=1).count() + Demande.objects.filter(date_cessation=INFINITY_DATE).filter(statut__id=2).count()
    services = Service.objects.filter(date_cessation=INFINITY_DATE)
    valeurs = [service.sollicitation_count() for service in services]
    couleurs = [service.couleur for service in services]
    noms = [service.intitule for service in services]
    donnees = {"valeurs":valeurs, "couleurs":couleurs, "noms":noms}
    demandes = Demande.objects.filter(date_cessation=INFINITY_DATE)
    agences = Agence.objects.filter(date_cessation=INFINITY_DATE)
    if user.profil.id == 2:
        valeurs = user.sollicitation()
        services = Service.objects.filter(date_cessation=INFINITY_DATE)
        couleurs = [service.couleur for service in services]
        noms = [service.intitule for service in services]
        donnees = {"valeurs":valeurs, "couleurs":couleurs, "noms":noms}
    
    if user.profil.id == 3:
        valeurs = user.sollicitation_agence()
        services = Service.objects.filter(date_cessation=INFINITY_DATE)
        couleurs = [service.couleur for service in services]
        noms = [service.intitule for service in services]
        donnees = {"valeurs":valeurs, "couleurs":couleurs, "noms":noms}
    
    
    return render(request, 'index.html', 
                  {"utilisateur": user,
                   "error": error,
                   "success":success,
                   "nb_agents": nb_agents,
                   "nb_agents_active": nb_agents_active,
                   "nb_demandes":nb_demandes,
                   "nb_demandes_abouties":nb_demandes_abouties,
                   "nb_demandes_non_abouties":nb_demandes_non_abouties,
                   "nb_demandes_inities_ou_en_cours":nb_demandes_inities_ou_en_cours,
                   "donnees":donnees,
                   "demandes":demandes,
                   }
                  )

def login(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is not None:
        return redirect("/")
    if request.POST:
        login = request.POST['login']
        password = request.POST['password']
        try:
            user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(login=login, password=chiffrement_cesar(password, SECRET), can_connect=True)
        except:
            request.session['error'] = 'Login ou mot de passe incorrect'
            return redirect("/login")
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
    print(user_identifiant)
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    if request.POST:
        nom = request.POST.get('nom').upper()
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse')
        photo = request.FILES.get('photo')
        if photo == None:
            photo = user.photo
        password = request.POST.get('password')
        
        u = Utilisateur(photo=photo, code=user.code,nom=nom, prenom=prenom, agence=user.agence, telephone=telephone, email=email, adresse=adresse, login=user.login, password=chiffrement_cesar(password, SECRET), profil=user.profil,modifier_par=user.code)
        u.save()
        
        user.date_cessation = datetime.now()
        user.modifier_par = user.code
        user.save()
        request.session["user"] = u.id
        request.session["success"] = "Profil modifié avec succès"
        return redirect("/profil")
    return render(request, 'agents/profil.html',
                  {"utilisateur": user,
                   "error": error,
                   "success":success,
                   }
                  )
def liste_agence_leader(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    agents = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(profil=Profil.objects.get(id=3))
    return render(request, 'agence-lead/list.html',
                  {"utilisateur": user,
                   "error":error,
                   "success":success,
                   "agents": agents,
                   }
                  )

def ajout_agence_leader(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    max_date = datetime.now() - timedelta(days=18*365)
    agences = Agence.objects.filter(date_cessation=INFINITY_DATE)
    if request.POST:
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        email = request.POST['email']
        telephone = request.POST['telephone']
        adresse = request.POST['adresse']
        agence = Agence.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST['agence'])
        profil = Profil.objects.get(id=3)
        login = request.POST['login']
        password = generate_strong_password()
        code = generate_code("UTL", Utilisateur.real_number()+1)
        modifier_par = user.code
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(login=login)
            request.session['error'] = 'Le login doit être unique.'
            return redirect("/agence-leader/list")
        except:
            pass
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(profil=profil).get(agence=agence)
            request.session['error'] = 'Il ne peut y avoir plusieurs chefs pour une même agence.'
            return redirect("/agence-leader/list")
        except:
            pass
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(nom=nom, prenom=prenom)
            request.session['error'] = 'Un utilisateur ayant le même nom et le même prénom existe déjà.'
            return redirect("/agence-leader/list")
        except:
            pass
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(email=email)
            request.session['error'] = 'Email déjà utilisé'
            return redirect("/agence-leader/list")
        except:
            pass
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(telephone=telephone)
            request.session['error'] = 'Telephone déjà utilisé'
            return redirect("/agence-leader/list")
        except:
            pass
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(date_naissance__gt=max_date)
            request.session['error'] = 'Date invalide'
            return redirect("/agence-leader/list")
        except:
            pass
        u = Utilisateur(code=code,nom=nom, prenom=prenom, agence=agence, telephone=telephone, email=email, adresse=adresse, login=login, password=chiffrement_cesar(password, SECRET), profil=profil,modifier_par=modifier_par)
        u.save()
        request.session["success"] = "Chef d'agence ajouté avec succès"
        return redirect("/agence-leader/list")
    return render(request, 'agence-lead/add.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "max_date":max_date.strftime("%Y-%m-%d"),
        "agences":agences,
    })

def edit_agence_leader(request, lead_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    lead = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=lead_id)
    agences = Agence.objects.filter(date_cessation=INFINITY_DATE)
    if request.POST:
        regeneratePass = bool(request.POST.get('regeneratePass', False))
        agence = Agence.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST['agence'])
        if regeneratePass:
            password = generate_strong_password()
        else:
            password = lead.true_pass()
        lead.date_cessation = datetime.now()
        lead.save()
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(agence=agence)
            request.session['error'] = 'Il ne peut y avoir plusieurs chefs pour une même agence.'
        except:
            pass
        u = Utilisateur(code=lead.code,nom=lead.nom, prenom=lead.prenom, agence=agence, telephone=lead.telephone, email=lead.email, adresse=lead.adresse, login=lead.login, password=chiffrement_cesar(password, SECRET), profil=lead.profil,modifier_par=user.code)
        u.save()
        lead.date_cessation = datetime.now()
        lead.modifier_par = user.code
        lead.save()
        request.session['success'] = f"Réaffectation effectuée avec succès"
        
        return redirect("/agence-leader/list")
    return render(request, 'agence-lead/edit.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "agent":lead,
        "agences":agences,
    })

def delete_agence_leader(request, lead_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    lead = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=lead_id)
    lead.date_cessation = datetime.now()
    lead.save()
    request.session['success'] = "Chef d'agence supprimé avec succès"
    return redirect("/agence-leader/list")

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
        login = request.POST['login']
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        email = request.POST['email']
        telephone = request.POST['telephone']
        adresse = request.POST['adresse']
        agence = Agence.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST['agence'])
        profil = Profil.objects.get(libelle="AGENT")
        password = generate_strong_password()
        code = generate_code("UTL", Utilisateur.real_number()+1)
        modifier_par = user.code
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(login=login)
            request.session['error'] = 'Un utilisateur doit avoir un login unique.'
            return redirect("/agents/list")
        except:
            pass
        try:
            Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(nom=nom, prenom=prenom)
            request.session['error'] = 'Un utilisateur ayant le même nom et le même prénom existe déjà.'
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
        u = Utilisateur(code=code,nom=nom, prenom=prenom, agence=agence, telephone=telephone, email=email, adresse=adresse, login=login, password=chiffrement_cesar(password, SECRET), profil=profil,modifier_par=modifier_par)
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
    if request.POST:
        regeneratePass = bool(request.POST.get('regeneratePass', False))
        
        agence = Agence.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST['agence'])
        modifier_par = user.code
        profil = Profil.objects.get(libelle="AGENT")
        if regeneratePass:
            password = generate_strong_password()
        else:
            password = agent.true_pass()
        u = Utilisateur(code=agent.code,nom=agent.nom, prenom=agent.prenom, agence=agence, telephone=agent.telephone, email=agent.email, adresse=agent.adresse, login=agent.login, password=chiffrement_cesar(password, SECRET), profil=profil,modifier_par=modifier_par)
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
    }
    )

def delete_agent(request, agent_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    try:
        agent = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=agent_id)
        agent.date_cessation = datetime.now()
        agent.save()
    except:
        request.session['error'] = "Agent inexistant"
    return redirect("/agents/list")
    


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
        
        try:
            Agence.objects.filter(date_cessation=INFINITY_DATE).get(intitule=intitule)
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
        code = generate_code("AGC", Agence.real_number()+1)
        modifier_par = user.code
        agence = Agence(code = code, modifier_par =modifier_par ,site=site, intitule=intitule)
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
        agence.date_cessation = datetime.now()
        agence.modifier_par = user.code
        agence.save()
        
        try:
            Agence.objects.filter(date_cessation=INFINITY_DATE).get(intitule=intitule)
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
        new_agence = Agence(code = agence.code, modifier_par =modifier_par ,site=site, intitule=intitule)
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
        code = code = generate_code("ENT", Entite.real_number()+1)
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
        code = code = generate_code("STR", Structure.real_number()+1)
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
        montant = request.POST.get('montant', None)
        couleur = Service.generate_color()
        try:
            montant = float(montant)
        except:
            request.session['error'] = 'Le montant doit être un nombre.'
            return redirect("/service/list")
        try:
            Service.objects.filter(date_cessation=INFINITY_DATE).get(intitule=intitule)
            request.session['error'] = 'Le service existe déjà.'
        except:
            code = code = generate_code("SRV", Service.real_number()+1)
            service = Service(code=code, intitule=intitule, montant=montant, couleur=couleur, modifier_par=user.code, structure=structure)
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
        montant = request.POST.get('montant', None)
        structure = Structure.objects.filter(date_cessation=INFINITY_DATE).get(code=structure)
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
        new_service = Service(code=service.code, intitule=intitule, couleur=service.couleur, modifier_par=user.code, structure=structure, montant=montant)
        
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
            code = code = generate_code("OPT", OptionSupplementaire.real_number()+1)
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
    demandes = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(agent__code=user.code).order_by('-id')
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
    success = request.session.pop('success', None)
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
            
            code = generate_code("DEM", Demande.real_number()+1)
            code_client = generate_code("CLIENT",Client.real_number()+1)
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
                    code = generate_code("OPTDEM", OptionSupplementaireDemande.real_number()+1)
                    option = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE).get(id=int(opt.replace("nb", "")))
                    optionSupDemand = OptionSupplementaireDemande(demande=demande, option_supplementaire=option, nombre=nb, code=code, modifier_par=user.code)
                    optionSupDemand.save()
        else:
            client = Client.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST["client"])
            service = Service.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST["service"])
            
            code = generate_code("DEM", Demande.real_number()+1)
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
                    code = generate_code("OPTDEM", OptionSupplementaireDemande.real_number()+1)
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

def ajout_demande_new_client(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    services = Service.objects.filter(date_cessation=INFINITY_DATE)
    options_sup = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE)
    if request.POST:
        if True:
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
            
            code = generate_code("DEM", Demande.real_number()+1)
            code_client = generate_code("CLIENT",Client.real_number()+1)
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
                    code = generate_code("OPTDEM", OptionSupplementaireDemande.real_number()+1)
                    option = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE).get(id=int(opt.replace("nb", "")))
                    optionSupDemand = OptionSupplementaireDemande(demande=demande, option_supplementaire=option, nombre=nb, code=code, modifier_par=user.code)
                    optionSupDemand.save()
            request.session['success'] = "La demande a bien été enregistrée."
        return redirect("/demande/list")
    
    return render(request, 'demande/add_new_client.html',
                  {
                      "utilisateur": user,
                      "error": error,
                      "success": success,
                      'services': services,
                      "options_sup":options_sup,
                   })

def ajout_demande_old_client(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    services = Service.objects.filter(date_cessation=INFINITY_DATE)
    options_sup = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE)
    clients = Client.objects.filter(date_cessation=INFINITY_DATE)
    if request.POST:
        if True:
            client = Client.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST["client"])
            service = Service.objects.filter(date_cessation=INFINITY_DATE).get(code=request.POST["service"])
            
            code = generate_code("DEM", Demande.real_number()+1)
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
                    code = generate_code("OPTDEM", OptionSupplementaireDemande.real_number()+1)
                    option = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE).get(id=int(opt.replace("nb", "")))
                    optionSupDemand = OptionSupplementaireDemande(demande=demande, option_supplementaire=option, nombre=nb, code=code, modifier_par=user.code)
                    optionSupDemand.save()
            request.session['success'] = "La demande a bien été enregistrée."
        return redirect("/demande/list")
    return render(request, 'demande/add_old_client.html',
                  {
                      "utilisateur": user,
                      "error": error,
                      "success": success,
                      "clients":clients,
                      'services': services,
                      "options_sup":options_sup,
                   })

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
                    code = generate_code("OPTDEM", OptionSupplementaireDemande.real_number()+1)
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
            return redirect(f"/demande/view_date/{year}/{month}/{day}/")
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
        demandes = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(agent__code__in=agents.filter(date_cessation=INFINITY_DATE).values_list('code', flat=True).distinct())
    return render(request, 'demande/search.html',
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
        demandes = Demande.objects.filter(date_cessation=INFINITY_DATE).filter(client__code=client.code)
    return render(request, 'demande/search.html',
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
    return render(request, 'demande/search.html',
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

def historique_demande(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    demandes_code = Demande.objects.values_list('code', flat=True).distinct()
    demandes = []
    for code in demandes_code:
        demande = Demande.objects.filter(code=code).last()
        demandes.append(demande)
    return render(request, 'historique/demande.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "demandes":demandes,
    })

def histo_agence_agent(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    agences = Agence.objects.filter(date_cessation=INFINITY_DATE)
    agents = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(agence__in=agences).filter(profil__id=2)
    if request.POST:
        if "agent" in request.POST:
            code_agent = request.POST.get("agent", None)
            return redirect(f"/historique/agent/{code_agent}")
        elif "agence" in request.POST:
            code_agence = request.POST.get("agence", None)
            return redirect(f"/historique/agence/{code_agence}")
        else:
            return redirect("/historique/agence-agent")
    return render(request, 'historique/agence_agent.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "agences":agences,
        "agents":agents,
    })

def historique_demande_by_agence(request, agence_code):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
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
        demandes_code = Demande.objects.filter(agent__code__in=agents.filter(date_cessation=INFINITY_DATE).values_list('code', flat=True).distinct()).values_list('code', flat=True).distinct()
        demandes = []
        for code in demandes_code:
            demande = Demande.objects.filter(code=code).last()
            demandes.append(demande)
    return render(request, 'historique/demande.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "demandes":demandes,
    })

def historique_demande_by_agent(request, agent_code):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    demandes = Demande.objects.filter(agent__code=agent_code).filter(date_cessation=INFINITY_DATE).order_by('-date_creation')
    return render(request, 'historique/demande.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "demandes":demandes,
    })

def stat_agence_agent(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    agences = Agence.objects.filter(date_cessation=INFINITY_DATE)
    agents = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(agence__in=agences).filter(profil__id=2)
    services = Service.objects.filter(date_cessation=INFINITY_DATE)
    valeurs = [service.sollicitation_count() for service in services]
    couleurs = [service.couleur for service in services]
    noms = [service.intitule for service in services]
    donnees = {"valeurs":valeurs, "couleurs":couleurs, "noms":noms}
    if request.POST:
        if "agent" in request.POST:
            code_agent = request.POST.get("agent", None)
            return redirect(f"/statistique/stat/agent/{code_agent}")
        elif "agence" in request.POST:
            code_agence = request.POST.get("agence", None)
            return redirect(f"/statistique/stat/{code_agence}")
        elif "agence_code" in request.POST:
            debut = request.POST.get("debut", None)
            fin = request.POST.get("fin", None)
            code_agence = request.POST.get("agence_code", None)
            return redirect(f"/statistique/stat/agence/period/{code_agence}/{debut}/{fin}")
        elif "debut" in request.POST:
            debut = request.POST["debut"]
            fin = request.POST["fin"]
            return redirect(f"/statistique/stat/period/{debut}/{fin}")
        
        else:
            return redirect("/statistique/agence-agent")
    return render(request, 'statistique/agence_agent.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "agences":agences,
        "agents":agents,
        "donnees":donnees,
    })

def stat_by_agence(request, agence_code):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    try:
        agence = Agence.objects.filter(date_cessation=INFINITY_DATE).get(code=agence_code)
    except:
        agence = None
        donnees = None
    if agence is not None:
        valeurs = agence.sollicitation()
        services = Service.objects.filter(date_cessation=INFINITY_DATE)
        couleurs = [service.couleur for service in services]
        noms = [service.intitule for service in services]
        donnees = {"valeurs":valeurs, "couleurs":couleurs, "noms":noms}
    return render(request, 'statistique/stat.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "donnees":donnees,
    })

def stat_by_agent(request, agent_code):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    try:
        agent = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(code=agent_code)
    except:
        agent = None
        donnees = None
    if agent is not None:
        valeurs = agent.sollicitation()
        services = Service.objects.filter(date_cessation=INFINITY_DATE)
        couleurs = [service.couleur for service in services]
        noms = [service.intitule for service in services]
        donnees = {"valeurs":valeurs, "couleurs":couleurs, "noms":noms}
    return render(request, 'statistique/stat.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "donnees":donnees,
    })

def stat_by_period(request, debut, fin):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    debut = datetime.strptime(debut, "%Y-%m-%d")
    debut = datetime.combine(debut.date(), time.min)
    fin = datetime.strptime(fin, "%Y-%m-%d")
    fin = datetime.combine(fin.date(), time.max)
    services = Service.objects.filter(date_cessation=INFINITY_DATE)
    valeurs = [val.sollicitation_by_period(debut, fin) for val in services]
    couleurs = [service.couleur for service in services]
    noms = [service.intitule for service in services]
    donnees = {"valeurs":valeurs, "couleurs":couleurs, "noms":noms}
    return render(request, 'statistique/stat.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "donnees":donnees,
    })

def stat_by_agence_and_period(request, agence_code, debut, fin):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    debut = datetime.strptime(debut, "%Y-%m-%d")
    debut = datetime.combine(debut.date(), time.min)
    fin = datetime.strptime(fin, "%Y-%m-%d")
    fin = datetime.combine(fin.date(), time.max)
    services = Service.objects.filter(date_cessation=INFINITY_DATE)
    valeurs = [val.solliciation_by_agence_and_period(agence_code, debut, fin) for val in services]
    couleurs = [service.couleur for service in services]
    noms = [service.intitule for service in services]
    donnees = {"valeurs":valeurs, "couleurs":couleurs, "noms":noms}
    return render(request, 'statistique/stat.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "donnees":donnees,
    })

def choix_period_stat_chef(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    if request.POST:
        debut = request.POST.get("debut", None)
        fin = request.POST.get("fin", None)
        return redirect(f"/stat_chef_agence_period/{debut}/{fin}")
    return render(request, 'statistique/chef_agence_period.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
    })

def stat_chef_agence_period(request, debut, fin):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    services = Service.objects.filter(date_cessation=INFINITY_DATE)
    agence_code = user.agence.code
    valeurs = [val.solliciation_by_agence_and_period(agence_code, debut, fin) for val in services]
    couleurs = [service.couleur for service in services]
    noms = [service.intitule for service in services]
    donnees = {"valeurs":valeurs, "couleurs":couleurs, "noms":noms}
    return render(request, 'statistique/stat1.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "donnees":donnees,
    })
    
def liste_client(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    clients = Client.objects.filter(date_cessation=INFINITY_DATE).order_by('nom')
    return render(request, 'client/list.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "clients":clients,
    })

def edit_client(request, client_id):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    client = Client.objects.filter(date_cessation=INFINITY_DATE).get(id=client_id)
    if request.POST:
        nom = request.POST.get("nom", None)
        prenom = request.POST.get("prenom", None)
        telephone = request.POST.get("telephone", None)
        adresse = request.POST.get("adresse", None)
        email = request.POST.get("email", None)
        date_naissance = request.POST.get("date_naissance", None)
        try:
            new_client = Client(nom=nom, prenom=prenom, telephone=telephone, adresse=adresse, email=email, date_naissance=date_naissance, code=client.code, modifier_par=user.code)
            new_client.save()
            client.date_cessation = datetime.now()
            client.save()
            success = "Les informations du client ont été modifiées avec succès"
            request.session["success"] = success
            return redirect("/client/list")
        except:
            error = "Veuillez remplir tous les champs"
            request.session["error"] = error
            return redirect(f"/client/edit/{client.id}")
    return render(request, 'client/edit.html',{
        "utilisateur": user,
        "error": error,
        "success":success,
        "client":client,
    })

def historique_clients(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    return render(request, "historique/clients.html",
                  {
                      "utilisateur": user,
                      "error": error,
                      "success":success,
                      "clients": Client.objects.filter(date_cessation=INFINITY_DATE).order_by('-date_cessation')
                  }
                  )

def generate_csv_services_rendus(request):
    datas = [["Date dernier statut", "Service", "Structure", "Agence", "Client", "Statut", "Montant total"]]
    demandes = Demande.objects.filter(date_cessation=INFINITY_DATE)
    for demande in demandes:
        datas.append([demande.date_creation_rep(), demande.service.intitule, f"{demande.service.structure.entite.denomination} - {demande.service.structure.denomination}", demande.agent.agence.intitule, demande.client.nom_prenom(), demande.statut.libelle, demande.montant_total()])
    
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quotechar='"')
    #writer = csv.writer(codecs.getwriter('utf-8')(output), delimiter=';', quotechar='"')
    
    for row in datas:
        writer.writerow(row)
        
    csv_data = output.getvalue()
    response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="Services_rendus.csv"'

    return response

def generate_csv_agence(request):
    datas = [["Date dernière modification", "Dénomination", "Site"]]
    agences = Agence.objects.filter(date_cessation=INFINITY_DATE)
    for agence in agences:
        datas.append([agence.date_creation_rep(), agence.intitule, agence.site])
    
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quotechar='"')
    #writer = csv.writer(codecs.getwriter('utf-8')(output), delimiter=';', quotechar='"')
    
    for row in datas:
        writer.writerow(row)
        
    csv_data = output.getvalue()
    response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="Agences.csv"'

    return response

def generate_csv_agence_lead(request):
    datas = [["Date dernière modification", "Login", "Nom", "Prénom", "Email", "Téléphone", "Adresse", "Agence"]]
    agents = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(profil=Profil.objects.get(id=3))
    
    for agent in agents:
        datas.append([agent.date_creation_rep(), agent.login, agent.nom, agent.prenom, agent.email, agent.telephone, agent.adresse, agent.agence.intitule])
    
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quotechar='"')
    #writer = csv.writer(codecs.getwriter('utf-8')(output), delimiter=';', quotechar='"')
    
    for row in datas:
        writer.writerow(row)
        
    csv_data = output.getvalue()
    response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="Chefs agences.csv"'

    return response

def generate_csv_agent(request):
    datas = [["Date dernière modification", "Login", "Nom", "Prénom", "Email", "Téléphone", "Adresse", "Agence"]]
    agents = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).filter(profil=Profil.objects.get(id=2))
    
    for agent in agents:
        datas.append([agent.date_creation_rep(), agent.login, agent.nom, agent.prenom, agent.email, agent.telephone, agent.adresse, agent.agence.intitule])
    
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quotechar='"')
    #writer = csv.writer(codecs.getwriter('utf-8')(output), delimiter=';', quotechar='"')
    
    for row in datas:
        writer.writerow(row)
        
    csv_data = output.getvalue()
    response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="Agents.csv"'

    return response

def generate_csv_entite(request):
    datas = [["Date dernière modification", "Dénomination"]]
    entites = Entite.objects.filter(date_cessation=INFINITY_DATE)
    
    for entite in entites:
        datas.append([entite.date_creation_rep(), entite.denomination])
    
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quotechar='"')
    #writer = csv.writer(codecs.getwriter('utf-8')(output), delimiter=';', quotechar='"')
    
    for row in datas:
        writer.writerow(row)
        
    csv_data = output.getvalue()
    response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="Entités.csv"'

    return response

def generate_csv_structure(request):
    datas = [["Date dernière modification", "Dénomination", "Entité"]]
    structures = Structure.objects.filter(date_cessation=INFINITY_DATE)
    
    for structure in structures:
        datas.append([structure.date_creation_rep(), structure.denomination, structure.entite.denomination])
    
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quotechar='"')
    #writer = csv.writer(codecs.getwriter('utf-8')(output), delimiter=';', quotechar='"')
    
    for row in datas:
        writer.writerow(row)
        
    csv_data = output.getvalue()
    response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="Structures.csv"'

    return response

def generate_csv_service(request):
    datas = [["Date dernière modification", "Intitulé", "Montant", "Structure", "Entité"]]
    services = Service.objects.filter(date_cessation=INFINITY_DATE)
    
    for service in services:
        datas.append([service.date_creation_rep(), service.intitule, service.montant, service.structure.denomination, service.structure.entite.denomination])
    
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quotechar='"')
    #writer = csv.writer(codecs.getwriter('utf-8')(output), delimiter=';', quotechar='"')
    
    for row in datas:
        writer.writerow(row)
        
    csv_data = output.getvalue()
    response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="Services.csv"'

    return response

def generate_csv_prestations(request):
    datas = [["Date dernière modification", "Dénomination", "Montant"]]
    options = OptionSupplementaire.objects.filter(date_cessation=INFINITY_DATE)
    
    for option in options:
        datas.append([option.date_creation_rep(), option.libelle, option.montant])
    
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quotechar='"')
    #writer = csv.writer(codecs.getwriter('utf-8')(output), delimiter=';', quotechar='"')
    
    for row in datas:
        writer.writerow(row)
        
    csv_data = output.getvalue()
    response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="Prestations Poste.csv"'

    return response

def validate_cashflow_day(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    today_debut = premiere_heure_jour()
    today_fin = derniere_heure_jour()
    demandes = Demande.objects.filter(date_creation__gt=today_debut, date_creation__lt=today_fin).filter(agent__agence__code=user.agence.code)
    total_of_day = 0
    for demande in demandes:
        total_of_day += demande.montant_percu_today()
    
    return render(request, "validation/today.html",
                  {'utilisateur': user,
                   'error': error,
                   'success': success,
                   "demandes": demandes,
                   "today_debut":today_debut,
                   "today_fin":today_fin,
                   "total_of_day":total_of_day
                   })

def valider_day(request):
    user_identifiant = request.session.get('user')
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    today_debut = premiere_heure_jour()
    today_fin = derniere_heure_jour()
    demandes = Demande.objects.filter(date_creation__gt=today_debut, date_creation__lt=today_fin).filter(agent__agence__code=user.agence.code)
    total_of_day = 0
    for demande in demandes:
        total_of_day += demande.montant_percu_today()
    validation = Validation(validate=True, validator=user, agence=user.agence, montant=total_of_day)
    validation.save()
    for demande in demandes:
        validationDemande = ValidationDemande(validation=validation, demande=demande)
        validationDemande.save()
    return redirect('/logout')

def invalider_day(request):
    user_identifiant = request.session.get('user')
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    today_debut = premiere_heure_jour()
    today_fin = derniere_heure_jour()
    demandes = Demande.objects.filter(date_creation__gt=today_debut, date_creation__lt=today_fin).filter(agent__agence__code=user.agence.code)
    total_of_day = 0
    for demande in demandes:
        total_of_day += demande.montant_percu_today()
    validation = Validation(validator=user, agence=user.agence, montant=total_of_day)
    validation.save()
    for demande in demandes:
        validationDemande = ValidationDemande(validation=validation, demande=demande)
        validationDemande.save()
    return redirect('/logout')

def view_validations(request):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    validations = Validation.objects.all().order_by('-day')
    if request.POST:
        if "agence_code" in request.POST:
            debut = request.POST.get("debut", None)
            fin = request.POST.get("fin", None)
            code_agence = request.POST.get("agence_code", None)
            return redirect(f"/view_validations/agence/period/{code_agence}/{debut}/{fin}")
        else:
            debut = request.POST.get("debut", None)
            fin = request.POST.get("fin", None)
            return redirect(f"/view_validations/period/{debut}/{fin}")
    return render(request, "validation/view.html",
                  {'utilisateur': user,
                   'error': error,
                   'success': success,
                   'validations':validations,
                   'agences':Agence.objects.filter(date_cessation=INFINITY_DATE),
                   })

def validation_by_agence_period(request,code_agence, debut, fin):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    debut = datetime.strptime(debut, "%Y-%m-%d")
    debut = datetime.combine(debut.date(), time.min)
    fin = datetime.strptime(fin, "%Y-%m-%d")
    fin = datetime.combine(fin.date(), time.max)
    validations =  Validation.objects.filter(day__range=(debut, fin)).filter(agence__code=code_agence).order_by('-day')
    return render(request, "validation/other_view.html",
                  {'utilisateur': user,
                   'error': error,
                   'success': success,
                   'validations':validations,
                   })

def validation_by_period(request, debut, fin):
    user_identifiant = request.session.get('user')
    error = request.session.pop('error', None)
    success = request.session.pop('success', None)
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.filter(date_cessation=INFINITY_DATE).get(id=user_identifiant)
    debut = datetime.strptime(debut, "%Y-%m-%d")
    debut = datetime.combine(debut.date(), time.min)
    fin = datetime.strptime(fin, "%Y-%m-%d")
    fin = datetime.combine(fin.date(), time.max)
    validations =  Validation.objects.filter(day__range=(debut, fin)).order_by('-day')
    return render(request, "validation/other_view.html",
                  {'utilisateur': user,
                   'error': error,
                   'success': success,
                   'validations':validations,
                   })