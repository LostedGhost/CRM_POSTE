from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path(r'', views.index, name="home"),
    path(r'login', views.login, name="login"),
    path(r'logout', views.logout, name="logout"),
    path(r'agents/list', views.liste_agent, name="liste_agent"),
    path(r'agents/add', views.ajout_agent, name="ajout_agent"),
    path(r'agents/addMany', views.add_many_agents, name="add_many_agents"),
    
]