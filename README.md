# test_ddr_api

Ce programme a pour but d'exécuter les tests de fonctionnalités des appels des différents API qui sont un des éléments de base de la 
[Stratégie de tests logiciels de l'équipe du DDR.](https://github.com/federal-geospatial-platform/project_management/tree/main/testing_strategy)

Lorsqu'un logiciel contient avec des point d'entrées original pour une ou plusieurs interfaces de proggramation d'application, 
il est impératif de créer des tester ces points d'entrées en utilisant la plateforme de tests 
[Postman.](https://www.postman.com/).  Une fois la ou les collections terminées et opérationnelles dans Postman vous devez exporter 
ces collections (*.json) et les copier dans le répertoire /newman. Vous devez par la suite mettre à jour
le fichier de configuration YMAL et republier dans le fichier docker.

# Le fichier YMAL

Le programme test_ddr_api est configurable via un YAML. Cette section décrit le contenu de ce fichier.

 - mode: **internal** or **external** : Utilisation des adresses internes ou externes pour les appels http.
 - email:
    - from: L'adresse courriel de la personne qui envoie le courriel
    - to: Liste des adresses couriels qui vont recevoir le courriel
    - host: Le nom du host qui gère le serveur de courrriel
    - user: Le nom de l'usager
    - password: Le mot de passe de l'usager
    - port: Le numéro de port
    - timeout: Le nombre de secondes pour le timeout
    - tsl: Fanion True/False pour le protocole de sécurité
  - log: Le nom di fichier log (adresse relative ou absolue)
  - collection
      - *nom de la collection*: Le nom du fichier JSON de la collection Post (sans l'extension .json)
        - request: Requête newman qui sera exécutée
        - var_url: Nom de la variable de collection contenant url des requêtes (défini dans la partie collection)
        - url_internal: Url de la requête interne
    
Vous trouverez ci-dessous un exemple de fichier de configuration YAML

```
mode: internal 
email: 
  from: bergeronpilon@gmail.com 
  to: [bergeronpilon@gmail.com] 
  host: email-smtp.ca-central-1.amazonaws.com 
  user: abc123 
  password: abc123
  port: 587
  timeout: 10
  tls: True
log: ../log/API_test.log
collections:
  PyGeoAPI:
    request: newman run ../newman/PyGeoAPI.json -k -r html,json
    var_url: urlPyGeoApi
    url_internal: http://10.68.130.138:5000/openapi
```
