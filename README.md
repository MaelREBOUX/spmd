# spmd

Scripts en lien à de traitements de données dans le cadre du Service Public Métropolitain de la Donnée de Rennes ([SPMD](http://metropole.rennes.fr/actualites/institutions-citoyennete/institution/le-service-public-de-la-donnee-en-6-questions/)).

## `extract_infos_sandre_xml.py`

Ce script permet de lire un fichier contenant des données au format [SANDRE](http://www.sandre.eaufrance.fr/).

Utilisation : ```extract_infos_sandre_xml.py  monfichier_sandre.xml```

Le script extrait les informations générales puis va lister tous les paramètres contenus dans le fichier.

```
Extraction des informations du fichier SANDRE .\test.xml

Scénario : Autosurveillance des systèmes de collecte et de traitement des eaux usées d'origine urbaine

date de début des données : 2016-01-01
date de fin des données   : 2016-05-31

code SANDRE de la station : 0435047S0003
Nom de la station dans le fichier : ST Bruz
Détails de la station dans le SI Eau  : http://www.sandre.eaufrance.fr/urn.php?urn=urn:sandre:donnees:SysTraitementEauxUsees:FRA:code:0435047S0003:::::xml

Extraction des infos sur les mesures et les paramètres
1 point(s) de mesure trouvé(s)

station 1
0242900100 : Boue produite (A6)
  5 prélèvements trouvés
    5 analyses trouvées
    Paramètres trouvés :
      - Matière sèche (MS) - Assainissement  | unité : kilogramme
```

En plus de la sortie console, un fichier contenant ces informations est écrit.



