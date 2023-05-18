# test_ddr_api

Ce programme a pour but d'exécuter les tests de fonctionnalités des appels des différents API qui sont un des éléments de base de la 
[Stratégie de tests logiciels de l'équipe du DDR.](https://github.com/federal-geospatial-platform/project_management/tree/main/testing_strategy)

Lorsqu'un logiciel contient avec des point d'entrées original pour une ou plusieurs interfaces de proggramation d'application, 
il est impératif de créer des tester ces points d'entrées en utilisant la plateforme de tests 
[Postman.](https://www.postman.com/).  ???Bonnes pratiques pour tester

# Le fichier YMAL

Le programme test_ddr_api est configurable via un YAML. Cette section décrit le contenu de ce fichier.

`mode: internal 
email: 
  from: bergeronpilon@gmail.com 
  to: [bergeronpilon@gmail.com] 
  host: email-smtp.ca-central-1.amazonaws.com 
  user: AKIARHK2ZDWAX5LTKCJH 
  password: BCpDDYnkVsrj8gvCTu7LliMq8+ie4C/JB6QZAEByLuVK
  port: 587
  timeout: 10
  tls: True
log: ../log/API_test.log
collections:
  PyGeoAPI:
    request: newman run ../newman/PyGeoAPI.json -k -r html,json
    var_url: urlPyGeoApi
    url_internal: http://10.68.130.138:5000/openapi`
