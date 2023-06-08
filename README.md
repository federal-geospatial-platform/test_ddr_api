


# Introduction

Le programme *test_ddr_api* a pour but d'exécuter les tests de fonctionnalités i.e. les appels aux différents API qui sont un des éléments de base de la 
[Stratégie de tests logiciels de l'équipe du DDR.](https://github.com/federal-geospatial-platform/project_management/tree/main/testing_strategy)

# Postman

Lorsqu'un logiciel contient des point d'entrées pour une ou plusieurs interfaces de programmation d'application (API), 
il est impératif de créer le code qui permettra de tester ces points d'entrées en utilisant la plateforme de tests 
[Postman.](https://www.postman.com/). Une fois les tests terminées et opérationnelles dans Postman vous devez exporter 
ces collections (*.json) et les copier dans le répertoire /newman du répertoire [github](https://github.com/federal-geospatial-platform/project_management/tree/main/testing_strategy). 
Vous devez au besoin mettre à jour le fichier de configuration YAML /python/config.yaml pour inclure cette nouvelle collection 
et recréer le fichier docker.

Si vous devez mettre à jour une collection de points d'entrées existentes, vous devrez importer le ou les fichiers *.json dans Postman. 
Ajouter et/ou mettre à jour les nouveaux points d'entrées et exporter de nouveau le fichier *.json dans le répertoire 
/newman de [github](https://github.com/federal-geospatial-platform/project_management/tree/main/testing_strategy).  

Pour pouvoir être exécuter dans l'environnement Postman la majorité des points d'entrées nécessitent une autentification 
i.e. un nonm d'usager et un mot de passe vers la base de données du DDR. Ces informations sont privés à la personne qui 
développe et sont emmagasinés dans l'environnement des variables Globals de Postman. Deux variables *username* et 
*password* doivent être créés pour contenir les informations permettant de se connecter er d'exécuter les différents 
points d'entrées (voir image ci-dessous).  

**Note importante: Le fichier Globals contant l'autentification pour la base de données ne doit jamais être transféré dans
GitHub car il contient des informations sensibles.**

![img.png](img.png)

# Fichier de configuration YAML

Le programme /python/test_ddr_api.py est configurable via un fichier YAML. Cette section décrit le contenu de ce fichier.

 - mode: **url_internal** or **url_external** : Utilisation des adresses internes (adresses IP ex.: 10.192.124.185) ou externes pour les appels http.
 - email:
    - from: L'adresse courriel de la personne qui envoie le courriel
    - to: Liste des adresses courriels qui vont recevoir le courriel
    - host: Le nom du host qui gère le serveur de courrriel
    - port: Le numéro de port
    - timeout: Le nombre de secondes pour le timeout
    - tsl: Fanion True/False pour le protocole de sécurité
  - log: Le nom du fichier log (adresse relative ou absolue)
  - collection
      - *nom de la collection*: Le nom du fichier JSON de la collection Postman (sans l'extension .json)
        - request: Requête newman qui sera exécutée
        - var_url: Nom de la variable de collection contenant url des requêtes (défini dans la partie collection)
        - url_internal: Url de la requête interne
    
Vous trouverez ci-dessous un exemple de fichier de configuration YAML

```
mode: url_internal 
email: 
  from: bergeronpilon@gmail.com 
  to: [bergeronpilon@gmail.com] 
  host: email-smtp.ca-central-1.amazonaws.com 
  port: 587
  timeout: 10
  tls: True
log: ../log/API_test.log
  clip_zip_ship_api:
    request: newman run newman_path::clip_zip_ship_api.json -k -r html,json-summary
    var_url: urlPyGeoApi
    url_internal: http://10.68.130.138:5000/openapi
```

# Exécution des tests de fonctionnalités de l'API

## Exécution interactive

Voici les étapes nécessaires pour exécuter interactivement les tests de fonctionnalités de l'API dans l'environnement Windows:

 - se connecter sur une machine Windows AWS (il est possible d'exécuter le programme sur un ordinateur
de RNCan mais aucun courriel ne pourra être envoyé)
 - cloner l'environnement github: `git clone https://github.com/federal-geospatial-platform/test_ddr_api.git`
 - installer les environnemnts Javascript et Newman nécessaires à l'exécution:
   - télécharger et installer [Node.js](https://nodejs.org/en/download)
   - installer [Newman](https://github.com/postmanlabs/newman): `npm install -g newman`
   - Installer [Newman Reporter HTML](https://www.npmjs.com/package/newman-reporter-html): `npm install -g newman-reporter-html`
   - installer [Newman Reporter Summary](https://www.npmjs.com/package/newman-reporter-json-summary): `npm install -g newman-reporter-json-summary`
   - se placer dans le répertoire `./python`
   - exécuter la commande `python test_ddr_api.py`

## Exécution Docker

Voici les étapes nécessaires pour créer le fichier docker des tests de fonctionnalités de l'API dans l'environnement Windows et ou Linux:

  - cloner l'environnement github: `git clone https://github.com/federal-geospatial-platform/test_ddr_api.git`
  - se déplacer dans le répertoire /test_drdr_api
  - créer l'image docker: `docker build -t test_ddr_api .`
  - exécuter l'image docker: `docker run test_ddr_api`

Note: 
  - Dans l'environnement Windows, l'outil: [Docker Desktop](https://www.docker.com/products/docker-desktop/) doit être installer
avant de tenter de créer des images dockers;
  - Dans l'environnement Linux, l'outil [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) doit être installer 
avant de tenter de créer des images dockers; 






