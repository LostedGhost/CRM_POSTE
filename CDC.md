# CRM Poste

Dans le cadre du monitoring des services des bornes d'accès, la Poste du Bénin a entrepris de mettre en place une plateforme de gestion de sa satisfaction client qui va lui permettre de gérer les demandes des clients et d'effectuer des analyses sur les différents services proposés en vu de l'amélioration desdits services.

## Règles de gestion

Il s'agit des règles qui jalonneront le suivi du projet.  
Entre autres, nous pouvons énumérer les règles suivantes:  
- [ ] Les utilisateurs sont soit des agents de terrain, soit l'administrateur (agent, admin)
- [ ] Un utilisateur est caractérisé par son nom d'utilisateur (unique) et son mot de passe
- [ ] Seul l'administrateur ajoute les agents de terrain
- [ ] L'administrateur peut retirer les droits d'activité à un agent
- [ ] Un agent de terrain appartient à une et une seule agence de la Poste
- [ ] Une agence a un code, une dénomination, une géolocalisation (longitude, latitude)
- [ ] Un agent peut enregistrer une demande client
- [ ] Un agent peut modifier une demande client mal renseignée
- [ ] Un agent peut supprimer une demande client qui n'a pas lieu d'être
- [ ] Un agent peut visualiser les demandes qu'il a eu à enregistrer
- [ ] Une demande client est caractérisée par son code, par le client, par le service sollicité et par l'agent qui a rédigé la demande
- [ ] Un service est une focntionnalité offerte par la Poste du Bénin à ses usagers via une borne d'accès
- [ ] Un service est caractérisé par son code, par sa dénomination, la structure éméttrice à laquelle il réfère
- [ ] Une entité est une entreprise en collaboration avec la Poste du Bénin et fournissant des services via les bornes d'accès
- [ ] Une entité a plusieurs structure éméttrice qui traitent de divers services suivant le cas
- [ ] Une structure éméttrice peut avoir ou non un ensemble de structures éméttrices
- [ ] Un administrateur peut visualiser la totalité des interactions effectuées avec le système
- [ ] Un administrateur peut visualiser les statistiques des demandes par services, par agence et par périodicité
- [ ] Un administrateur peut ajouter ou modifier ou supprimer un service
- [ ] Un administrateur peut ajouter ou modifier ou supprimer une entité
- [ ] Un administrateur peut ajouer ou modifier ou supprimer une structure émettrice
- [ ] Un administrateur peut définir ou modifier ou supprimer une agence
- [ ] Chaque demande client génère un ticket
- [ ] Chaque demande a un statut qui permet de suivre son avancée dans le système
- [ ] Un statut de demande est soit initié, soit en instance, soit abouti, soit non abouti
- [ ] Un client est enregistré une et une seule fois. A son arrivée les fois à venir, il fournit juste son numéro client.

## Contraintes techniques

- **Technologies**
  - Python
  - Django
  - HTML
  - CSS
  - Javascript
  - Bootstrap
  - Oracle

- **Rendu**
  - Ergonomie et responsivité
  - Accessible et dynamique
  - Charte graphique

- **Livraison**
  - Maintenances évolutives et correctives
  - Historisation des interactions
  - Documentation d'utilisation



