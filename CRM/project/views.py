from django.shortcuts import render
from django.shortcuts import redirect
import openpyxl
from .models import *

# Create your views here.

def index(request):
    user_identifiant = request.session.get('user')
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.get(id=user_identifiant)
    nb_agents = Utilisateur.objects.filter(is_deleted=False).filter(profil__libelle="AGENT").count()
    nb_agents_active = Utilisateur.objects.filter(is_deleted=False).filter(profil__libelle="AGENT").filter(is_active=True).count()
    return render(request, 'index.html', 
                  {"utilisateur": user,
                   "nb_agents": nb_agents,
                   "nb_agents_active": nb_agents_active,
                   }
                  )

def login(request):
    user_identifiant = request.session.get('user')
    if user_identifiant is not None:
        return redirect("/")
    if request.POST:
        login = request.POST['login']
        password = request.POST['password']
        try:
            user = Utilisateur.objects.get(login=login, password=chiffrement_cesar(password, SECRET))
        except:
            return render(request, 'login.html', {'error': 'Login ou mot de passe incorrect'})
        request.session['user'] = user.id
        user.is_active = True
        user.save()
        return redirect("/")
    return render(request, 'login.html')

def logout(request):
    user_identifiant = request.session.get('user')
    if user_identifiant is not None:
        user = Utilisateur.objects.get(id=user_identifiant)
        user.is_active = False
        user.save()
    request.session.clear()
    return redirect("/login")

def liste_agent(request):
    user_identifiant = request.session.get('user')
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.get(id=user_identifiant)
    agents = Utilisateur.objects.filter(profil__libelle="AGENT")
    return render(request, 'agents/list.html',
                  {"utilisateur": user,
                   "agents": agents,
                   }
                  )

def ajout_agent(request):
    user_identifiant = request.session.get('user')
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.get(id=user_identifiant)
    max_date = datetime.now() - timedelta(days=18*365)
    if request.POST:
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        date_naissance = request.POST['date_naissance']
        email = request.POST['email']
        telephone = request.POST['telephone']
        adresse = request.POST['adresse']
        profil = Profil.objects.get(libelle="AGENT")
        login = Utilisateur.generate_login()
        password = Utilisateur.generate_password()
        code = generate_code("UTL", Utilisateur.objects.count()+1)
        modifier_par = user.code
        try:
            Utilisateur.objects.get(nom=nom, prenom=prenom, date_naissance=date_naissance)
            return render(request, 'agents/add.html', {'error': 'Un utilisateur ayant le même nom, le même prénom et la même date de naissance existe déjà.'})
        except:
            pass
        try:
            Utilisateur.objects.get(email=email)
            return render(request, 'agents/add.html', {'error': 'Email déjà utilisé'})
        except:
            pass
        try:
            Utilisateur.objects.get(telephone=telephone)
            return render(request, 'agents/add.html', {'error': 'Téléphone déjà utilisé'})
        except:
            pass
        try:
            Utilisateur.objects.get(date_naissance__gt=max_date)
            return render(request, 'agents/add.html', {'error': 'Date invalide'})
        except:
            pass
        u = Utilisateur(code=code,nom=nom, prenom=prenom, date_naissance=date_naissance, telephone=telephone, email=email, adresse=adresse, login=login, password=chiffrement_cesar(password, SECRET), profil=profil,modifier_par=modifier_par)
        u.save()
        return redirect("/agents/list")
    return render(request, 'agents/add.html',{
        "utilisateur": user,
        "max_date":max_date.strftime("%Y-%m-%d"),
    })

def add_many_agents(request):
    user_identifiant = request.session.get('user')
    if user_identifiant is None:
        return redirect("/login")
    user = Utilisateur.objects.get(id=user_identifiant)
    if request.POST:
        usersFile = request.FILES["usersFile"]
        usersFile = AddUsersFiles(fichier_xl=usersFile)
        usersFile.save()
        classeur = openpyxl.load_workbook(str(settings.BASE_DIR) + usersFile.fichier_xl.url)
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
                  })