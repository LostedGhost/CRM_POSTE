# CRM Poste

Dans le cadre du monitoring des services des bornes d'accès, la Poste du Bénin a entrepris de mettre en place une plateforme de gestion de sa satisfaction client qui va lui permettre de gérer les demandes des clients et d'effectuer des analyses sur les différents services proposés en vue de l'amélioration desdits services.

## Règles de gestion

Il s'agit des règles qui jalonneront le suivi du projet.  
Entre autres, nous pouvons énumérer les règles suivantes:

- [X] Les utilisateurs sont soit des agents de terrain, soit l'administrateur (agent, admin)
- [X] Un utilisateur est caractérisé par son nom d'utilisateur (unique) et son mot de passe
- [X] Seul l'administrateur ajoute les agents de terrain
- [ ] L'administrateur peut retirer les droits d'activité à un agent
- [X] Un agent de terrain appartient à une et une seule agence de la Poste
- [X] Une agence a un code, une dénomination, une géolocalisation (longitude, latitude)
- [X] Un agent peut enregistrer une demande client
- [ ] Un agent peut modifier une demande client mal renseignée
- [X] Un agent peut supprimer une demande client qui n'a pas lieu d'être
- [X] Un agent peut visualiser les demandes qu'il a eu à enregistrer
- [X] Une demande client est caractérisée par son code, par le client, par le service sollicité et par l'agent qui a rédigé la demande
- [X] Un service est une fonctionnalité offerte par la Poste du Bénin à ses usagers via une borne d'accès
- [X] Un service est caractérisé par son code, par sa dénomination, la structure émettrice à laquelle il réfère
- [X] Une entité est une entreprise en collaboration avec la Poste du Bénin et fournissant des services via les bornes d'accès
- [X] Une entité a plusieurs structures émettrices qui traitent de divers services suivant le cas
- [X] Une structure émettrice peut avoir ou non un ensemble de structures émettrices
- [ ] Un administrateur peut visualiser la totalité des interactions effectuées avec le système
- [ ] Un administrateur peut visualiser les statistiques des demandes par services, par agence et par périodicité
- [X] Un administrateur peut ajouter ou modifier ou supprimer un service
- [X] Un administrateur peut ajouter ou modifier ou supprimer une entité
- [X] Un administrateur peut ajouer ou modifier ou supprimer une structure émettrice
- [X] Un administrateur peut définir ou modifier ou supprimer une agence
- [ ] Chaque demande client génère un ticket
- [X] Un client est enregistré une et une seule fois. A son arrivée les fois à venir, il fournit juste son numéro client.

## Contraintes techniques

- **Technologies**

  - Python
  - Django
  - HTML
  - CSS
  - Javascript
  - Bootstrap
- **Rendu**

  - Ergonomie e			t responsivité
  - Accessible et dynamique
  - Charte graphique
- **Livraison**

  - Maintenances évolutives et correctives
  - Historisation des interactions
  - Documentation d'utilisation
