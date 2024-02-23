from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path(r'', views.index, name="home"),
    path(r'login', views.login, name="login"),
    path(r'logout', views.logout, name="logout"),
    path(r'profil', views.profile, name="profile"),
    
    path(r'agents/list', views.liste_agent, name="liste_agent"),
    path(r'agents/add', views.ajout_agent, name="ajout_agent"),
    path(r'agents/edit/<int:agent_id>', views.reaffectation_agent, name="reaffectation_agent"),
    path(r'agents/addMany', views.add_many_agents, name="add_many_agents"),
    
    path(r'agence/list', views.liste_agences, name="liste_agences"),
    path(r'agence/add', views.ajout_agence, name="ajout_agence"),
    path(r'agence/edit/<int:agence_id>', views.edit_agence, name="edit_agence"),
    path(r'agence/delete/<int:agence_id>', views.delete_agence, name="delete_agence"),
    
    path(r'entite/list', views.liste_entite, name="liste_entite"),
    path(r'entite/add', views.ajout_entite, name="ajout_entite"),
    path(r'entite/edit/<int:entite_id>', views.modifier_entite, name="modifier_entite"),
    path(r'entite/delete/<int:entite_id>', views.delete_entite, name="delete_entite"),
    
    path(r'structure/list', views.liste_structure, name="liste_structure"),
    path(r'structure/add', views.ajout_structure, name="ajout_structure"),
    path(r'structure/edit/<int:struc_id>', views.edit_structure, name="edit_structure"),
    path(r'structure/delete/<int:struc_id>', views.delete_structure, name="delete_structure"),
    
    path(r'service/list', views.liste_services, name="liste_services"),
    path(r'service/add', views.ajout_service, name="ajout_service"),
    path(r'service/edit/<int:serv_id>', views.edit_service, name="edit_service"),
    path(r'service/delete/<int:serv_id>', views.delete_structure, name="delete_structure"),
    
    path(r'option/list', views.liste_option_sup, name="liste_option_sup"),
    path(r'option/add', views.ajout_option, name="ajout_option"),
    path(r'option/edit/<int:opt_id>', views.edit_option, name="edit_option"),
    path(r'option/delete/<int:opt_id>', views.delete_option, name="delete_option"),
    
    path(r'demande/list', views.liste_demande, name="liste_demande"),
    path(r'demande/add', views.ajout_demande, name="ajout_demande"),
    path(r'demande/focus/<int:dem_id>', views.suivre_demande, name="suivre_demande"),
    path(r'demande/other', views.other_demande, name="other_demande"),
    path(r'demande/view/<str:dem_code>', views.view_demande_by_code, name="view_demande_by_code"),
    path(r'demande/view_agence/<str:agence_code>', views.view_demande_by_agence, name="view_demande_by_agence"),
    path(r'demande/view_client/<str:client_code>', views.view_demande_by_client, name="view_demande_by_client"),
    path(r'demande/view_date/<int:year>/<int:month>/<int:day>/', views.view_demande_by_date, name="view_demande_by_date"),
    path(r'demande/edit/<int:dem_id>', views.edit_service, name="edit_service"),
    path(r'demande/delete/<int:dem_id>', views.delete_demande, name="delete_demande"),
    
    
]