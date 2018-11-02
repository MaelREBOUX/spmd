#-------------------------------------------------------------------------------
# Name:        Decouverte export XML SANDRE
#
# Purpose:     Le but de ce script est de lire un fichier de données XML afin de découvrir ce qu'il contient
#
# Author:      m.reboux
#
# Created:     08/10/2018
# Copyright:   (c) m.reboux 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# scénario
# 1. lecture du fichier XML ex : analyses sortie Station épuration (auto contrôle)
# 2. pour chaque point de mesure : identitification des paramètre analysés
# 3. sortie dans un fichier de synthèse

# utilisation de l'API http://www.sandre.eaufrance.fr/api-referentiel
# pour une station épuration : pas d'API
#  http://www.sandre.eaufrance.fr/urn.php?urn=urn:sandre:donnees:SysTraitementEauxUsees:FRA:code:0435047S0003:::::xml
# pour obtenir le nom des paramètres
# https://api.sandre.eaufrance.fr/referentiels/v1/parametre.xml?filter=<Filter><IS><Field>CdParametre</Field><Value>1313</Value></IS></Filter>

# problème dans le fichier SANDRE : le namespace n'a pas de prefixe alors on corrige le xml pour pouvoir le parser.


import os, sys
import argparse
from argparse import RawTextHelpFormatter
import configparser
from lxml import etree
import codecs
import requests
import random


# répertoire courant
script_dir = os.path.dirname(__file__)

# lecture du fichier de configuration
config = configparser.ConfigParser()
config.read( script_dir + '/config.ini')

# fichier de sortie
f_synthese = script_dir + "\\synthese_"

type_donnees = ""

# variables globales
mode_debug = False


# xml namespaces
cfg = {
  'ns': {
    'assai'   : u'http://xml.sandre.eaufrance.fr/scenario/fct_assain/3',
    'quesu'   : u'http://xml.sandre.eaufrance.fr/scenario/quesu/2'
  }
}

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def Logguer(logString):

  # cette fonction permet de sortir correctement les print() en mode dev (console python) et terminal

  if (mode_debug == False):
    # sortie console en UTF-8
    utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
    print( logString, file=utf8stdout)
  else:
    # sortie dans la console python
    print( logString )

  # on écrit aussi dans le fichier de synthèse
  with codecs.open(f_synthese, "a", "utf-8") as f:
    f.write(logString + "\n")
    f.close()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def xmlGetTextNodes(doc, xpath):
    """
    shorthand to retrieve serialized text nodes matching a specific xpath
    """
    return '|'.join(doc.xpath(xpath, namespaces=cfg['ns']))

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def ExtractionInfosGenerales():

  #Logguer("Extraction des infos générales sur le fichier")


  if (type_donnees == 'assai'):

    # ce que contient le fichier
    Scenario = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/Scenario/NomScenario/text()')
    # plage de dates des données
    DateDebutReference = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/Scenario/DateDebutReference/text()')
    DateFinReference = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/Scenario/DateFinReference/text()')

    # on écrit dans le fichier
    Logguer("Scénario : " + Scenario )
    Logguer("")
    Logguer("date de début des données : " + DateDebutReference )
    Logguer("date de fin des données   : " + DateFinReference )
    Logguer("")

    # les ouvrages / stations concernées
    # normalement : que 1. Si plus de 1 : on sort
    if ( len( xml_sandre_tree.xpath('/FctAssain/OuvrageDepollution', namespaces=cfg['ns']) ) != 1 ):
      Logguer( "Le fichier contient des données de plus d'un ouvrage : cela n'est pas autorisé" )
      Logguer( "FIN" )
    else:
      CdOuvrageDepollution = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/OuvrageDepollution/CdOuvrageDepollution/text()')
      NomOuvrageDepollution = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/OuvrageDepollution/NomOuvrageDepollution/text()')
      DetailXMLStation = "http://www.sandre.eaufrance.fr/urn.php?urn=urn:sandre:donnees:SysTraitementEauxUsees:FRA:code:" + CdOuvrageDepollution + ":::::xml"

      # on écrit dans le fichier
      Logguer("code SANDRE de la station : " + CdOuvrageDepollution)
      Logguer("Nom de la station dans le fichier : " + NomOuvrageDepollution )
      Logguer("Détails de la station dans le SI Eau  : " + DetailXMLStation )
      Logguer("")

      # puis on appelle la fonction qui va regarder les données
      Assai_ExtractionInfosMesures()
      pass


  elif (type_donnees == 'quesu'):

    # ce que contient le fichier
    Scenario = xmlGetTextNodes(xml_sandre_tree, '/QUESU/Scenario/NomScenario/text()')
    # plage de dates des données
    DateDebutReference = xmlGetTextNodes(xml_sandre_tree, '/QUESU/Scenario/DateDebutReference/text()')
    DateFinReference = xmlGetTextNodes(xml_sandre_tree, '/QUESU/Scenario/DateFinReference/text()')

    # on écrit dans le fichier
    Logguer("Scénario : " + Scenario )
    Logguer("")
    Logguer("date de début des données : " + DateDebutReference )
    Logguer("date de fin des données   : " + DateFinReference )
    Logguer("")

    # puis on appelle la fonction qui va regarder les données
    Quesu_ExtractionInfosMesures()
    pass


  #Logguer("fait")
  #Logguer("")


 # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def Assai_ExtractionInfosMesures():

  Logguer("Extraction des infos sur les mesures et les paramètres")

  # on compte le nb de PointMesure
  nbPointMesure = len( xml_sandre_tree.xpath('/FctAssain/OuvrageDepollution/PointMesure', namespaces=cfg['ns']) )

  Logguer( str(nbPointMesure) + " point(s) de mesure trouvé(s)" )

  # boucle sur les points de mesure
  f_to_write = ""
  idxMesure = 1
  while idxMesure <= nbPointMesure :
    NumeroPointMesure = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/OuvrageDepollution/PointMesure['+str(idxMesure)+']/NumeroPointMesure/text()')
    LbPointMesure = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/OuvrageDepollution/PointMesure['+str(idxMesure)+']/LbPointMesure/text()')

    Logguer("")
    Logguer( "station " + str(idxMesure) )
    Logguer( str(NumeroPointMesure) + ' : '+ LbPointMesure )

    # nb de prélèvements
    nbPrlvt = len( xml_sandre_tree.xpath('/FctAssain/OuvrageDepollution/PointMesure['+str(idxMesure)+']/Prlvt', namespaces=cfg['ns']) )
    Logguer( "  " + str(nbPrlvt) + " prélèvements trouvés" )

    # boucle sur les prélèvements
    idxPrlvt = 1
    nbTotalAnalyses = 0
    while idxPrlvt <= nbPrlvt :
      # nb d'analyses
      nbAnalyses = len( xml_sandre_tree.xpath('/FctAssain/OuvrageDepollution/PointMesure['+str(idxMesure)+']/Prlvt['+str(idxPrlvt)+']/Analyse', namespaces=cfg['ns']) )
      #Logguer( "    " + str(nbAnalyses) + " analyses trouvées" )

      # on déclare un tableau qui va stocker les couples paramètres|unités
      # pour ensuite dédoublonner
      listParam = []

      # boucle sur les analyses
      idxAnalyse = 1
      while idxAnalyse <= nbAnalyses :
        CdParametre = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/OuvrageDepollution/PointMesure['+str(idxMesure)+']/Prlvt['+str(idxPrlvt)+']/Analyse['+str(idxAnalyse)+']/Parametre/CdParametre/text()')
        CdUniteMesure = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/OuvrageDepollution/PointMesure['+str(idxMesure)+']/Prlvt['+str(idxPrlvt)+']/Analyse['+str(idxAnalyse)+']/UniteMesure/CdUniteMesure/text()')
        #Logguer( "      paramètre trouvé : " + str(CdParametre) + " | " + CdUniteMesure )

        # on stocke
        listParam.append([CdParametre,CdUniteMesure])
        # on compte
        nbTotalAnalyses += 1

        idxAnalyse += 1

      idxPrlvt += 1

    idxMesure += 1

    # on sort de la boucle sur les analyses
    Logguer( "    " + str(nbTotalAnalyses) + " analyses trouvées" )

    if nbTotalAnalyses > 0 :
      # on peut produire la liste des paramètres sans doublons
      listParamUnique = []
      i = 0

      for x in listParam:
        if x not in listParamUnique:
          listParamUnique.append(x)
      i += 1

      # et là seulement on interroge l'API pour avoir le nom du paramètre
      Parametre = RecupInfosParametre(CdParametre, CdUniteMesure)

      Logguer("    Paramètres trouvés :")
      Logguer( "      - " + Parametre )

  Logguer("")
  Logguer("------------------------------------------------------------")
  Logguer("")



 # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def Quesu_ExtractionInfosMesures():

  Logguer("Extraction des infos sur les mesures et les paramètres")

  # on compte le nb de CdStationMesureEauxSurface
  nbPointMesure = len( xml_sandre_tree.xpath('/QUESU/ResPC', namespaces=cfg['ns']) )

  Logguer( str(nbPointMesure) + " point(s) de mesure trouvé(s)" )

  nbTotalAnalyses = 0

  # boucle sur les points de mesure
  f_to_write = ""
  idxPtMesure = 1
  while idxPtMesure <= nbPointMesure :
    NumeroPointMesure = xmlGetTextNodes(xml_sandre_tree, '/QUESU/ResPC['+str(idxPtMesure)+']/CdStationMesureEauxSurface/text()')
    LbPointMesure = "TODO"

    Logguer("")
    Logguer( "station " + str(idxPtMesure) )
    Logguer( str(NumeroPointMesure) + ' : '+ LbPointMesure )

    # nb de prélèvements
    nbPrlvt = len( xml_sandre_tree.xpath('/QUESU/ResPC['+str(idxPtMesure)+']/PrelevementsPhysicoChimie', namespaces=cfg['ns']) )
    Logguer( "  " + str(nbPrlvt) + " prélèvements trouvés" )

    # boucle sur les prélèvements
    idxPrlvt = 1
    nbAnalysesStation = 0

    while idxPrlvt <= nbPrlvt :
      # nb d'analyses
      nbAnalyses = len( xml_sandre_tree.xpath('/QUESU/ResPC['+str(idxPtMesure)+']/PrelevementsPhysicoChimie['+str(idxPrlvt)+']/Analyse', namespaces=cfg['ns']) )
      #Logguer( "    " + str(nbAnalyses) + " analyses trouvées" )

      # on déclare un tableau qui va stocker les couples paramètres|unités
      # pour ensuite dédoublonner
      listParam = []

      # boucle sur les analyses
      idxAnalyse = 1
      while idxAnalyse <= nbAnalyses :
        CdParametre = xmlGetTextNodes(xml_sandre_tree, '/QUESU/ResPC['+str(idxPtMesure)+']/PrelevementsPhysicoChimie['+str(idxPrlvt)+']/Analyse['+str(idxAnalyse)+']/Parametre/CdParametre/text()')
        CdUniteMesure = xmlGetTextNodes(xml_sandre_tree, '/QUESU/ResPC['+str(idxPtMesure)+']/PrelevementsPhysicoChimie['+str(idxPrlvt)+']/Analyse['+str(idxAnalyse)+']/Unite/CdUniteReference/text()')
        #Logguer( "      paramètre trouvé : " + str(CdParametre) + " | " + CdUniteMesure )

        # on stocke
        listParam.append([CdParametre,CdUniteMesure])
        # on compte
        nbAnalysesStation += 1
        nbTotalAnalyses += 1

        idxAnalyse += 1

      idxPrlvt += 1

    idxPtMesure += 1


    # on sort de la boucle sur les analyses
    Logguer( "    " + str(nbAnalysesStation) + " analyses trouvées" )

    if nbAnalysesStation > 0 :
      # on peut produire la liste des paramètres sans doublons
      listParamUnique = []
      i = 0

      for x in listParam:
        if x not in listParamUnique:
          listParamUnique.append(x)
      i += 1

      # et là seulement on interroge l'API pour avoir le nom du paramètre
      #Parametre = RecupInfosParametre(CdParametre, CdUniteMesure)
      Parametre = "TODO : " + CdParametre + " ("+CdUniteMesure+")" #RecupInfosParametre(CdParametre, CdUniteMesure)

      Logguer("    Paramètres trouvés :")
      Logguer( "      - " + Parametre )


  Logguer("")
  Logguer("------------------------------------------------------------")
  Logguer( "  " + str(nbTotalAnalyses) + " analyses trouvées au total" )
  Logguer("------------------------------------------------------------")
  Logguer("")









  sys.exit()




  nbTotalAnalyses = 0

  # boucle sur les points de mesure
  f_to_write = ""
  idxPtMesure = 1
  while idxPtMesure <= nbPointMesure :
    NumeroPointMesure = xmlGetTextNodes(xml_sandre_tree, '/QUESU/ResPC['+str(idxPtMesure)+']/CdStationMesureEauxSurface/text()')
    LbPointMesure = "TODO"

    Logguer("")
    Logguer( "station " + str(idxPtMesure) )
    Logguer( str(NumeroPointMesure) + ' : '+ LbPointMesure )

    # on déclare un tableau qui va stocker les couples paramètres|unités
    # pour ensuite dédoublonner
    listParam = []

    # nb d'analyses pour le point de prélèvement
    nbAnalyses = len( xml_sandre_tree.xpath('/QUESU/ResPC['+str(idxPtMesure)+']/PrelevementsPhysicoChimie/Analyse', namespaces=cfg['ns']) )

    # boucle sur les analyses
    idxAnalyse = 1
    while idxAnalyse <= nbAnalyses :
      CdParametre = xmlGetTextNodes(xml_sandre_tree, '/QUESU/ResPC['+str(idxPtMesure)+']/PrelevementsPhysicoChimie/Analyse['+str(idxAnalyse)+']/Parametre/CdParametre/text()')
      CdUniteMesure = xmlGetTextNodes(xml_sandre_tree, '/QUESU/ResPC['+str(idxPtMesure)+']/PrelevementsPhysicoChimie/Analyse['+str(idxAnalyse)+']/Unite/CdUniteReference/text()')
      #Logguer( "    paramètre trouvé : " + str(CdParametre) + " | " + CdUniteMesure )

      # on stocke
      listParam.append([CdParametre,CdUniteMesure])
      # on compte
      nbTotalAnalyses += 1

      idxAnalyse += 1


    if nbAnalyses > 0 :
      # on peut produire la liste des paramètres sans doublons
      listParamUnique = []
      i = 0

      for x in listParam:
        if x not in listParamUnique:
          listParamUnique.append(x)
      i += 1

      # et là seulement on interroge l'API pour avoir le nom du paramètre
      Parametre = "TODO : " + CdParametre + " ("+CdUniteMesure+")" #RecupInfosParametre(CdParametre, CdUniteMesure)

      Logguer("    Paramètres trouvés :")
      Logguer( "      - " + Parametre )


    idxPtMesure += 1


    # on sort de la boucle sur les analyses
    Logguer( "  " + str(nbTotalAnalyses) + " analyses trouvées" )

  Logguer("")
  Logguer("------------------------------------------------------------")
  Logguer("")


  pass

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def RecupInfosParametre(code_parametre, code_unite_mesure):

  # on va appele l'API du SANDRE pour récupérer des infos sur le paramètre
  # on rajoute un nombre u hasard pour contourner le cache proxy
  url_api_sandre = "https://api.sandre.eaufrance.fr/referentiels/v1/parametre.xml?_"+ str(random.randrange(1, 100000)) + "&filter=%3CFilter%3E%3CIS%3E%3CField%3ECdParametre%3C/Field%3E%3CValue%3E"+code_parametre+"%3C/Value%3E%3C/IS%3E%3C/Filter%3E"

  # on ouvre une session
  r = requests.Session()

  # on voit si on est en mode proxy ou pas
  if (config.get('proxy', 'enable') == "true" ):
    # oui alors on va lire la configuration
    proxyConfig = {
      'http': ''+config.get('proxy','http')+'',
      'https': ''+config.get('proxy','https')+'',
    }
    r.proxies = proxyConfig


  # on récupère la réponse de lAPI qui est du XML
  try:
    # ceci désactive le message d'avertissement sur cetificat dans le texte de réponse
    requests.packages.urllib3.disable_warnings()
    # on peut maintenant lancer la requête. le verify c'est pour ne pas vérifier le certificat du proxy ou du site distant
    xml_content = r.get(url_api_sandre, verify=False).text

    # on corrige le xml reçu
    xml_corrige = CorrigerXmlSandre(xml_content)

    # on parse ce xml
    xml_tree = etree.XML(xml_corrige)

    # on doit récupérer 2 choses : le libellé du paramètre et son unité de mesure

    # libellé du paramètre : facile
    LibParam = xmlGetTextNodes(xml_tree, '/REFERENTIELS/Referentiel/Parametre/NomParametre/text()')

    # unité : il peut y avoir plusieurs unités pour un paramètre. Il faut matcher la bonne
    nbUnite = len( xml_tree.xpath('/REFERENTIELS/Referentiel/Parametre/ParametreChimique/ParChimiqueQuant/UniteReference', namespaces=cfg['ns']) )
    LbUniteReference = "inconnue"
    # on boucle pour trouver celle utilisée
    i = 1
    while i <= nbUnite :
      codeUnite = xmlGetTextNodes(xml_tree, '/REFERENTIELS/Referentiel/Parametre/ParametreChimique/ParChimiqueQuant/UniteReference['+str(i)+']/CdUniteReference/text()')
      if codeUnite == code_unite_mesure :
        # on le récupère
        LbUniteReference =  xmlGetTextNodes(xml_tree, '/REFERENTIELS/Referentiel/Parametre/ParametreChimique/ParChimiqueQuant/UniteReference['+str(i)+']/LbUniteReference/text()')
        # on sort
        break
      i += 1

    # on retourne le tout
    return( LibParam + "  | unité : " + LbUniteReference  )
    #print("      - " + LibParam + "  | unité : " + LbUniteReference + "")

  except Exception as err:
    print( str(err) )

  r.close()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def CorrigerXmlSandre(xml):

  # cette petite fonction ajoute un préfixe aux namespaces du SANDRE
  # sinon ça plante le parsing par lkml

  if (type_donnees == 'assai'):
    xml_corrige = xml.replace("xmlns=\"http://xml.sandre.eaufrance.fr/","xmlns:assai=\"http://xml.sandre.eaufrance.fr/")
  elif (type_donnees == 'quesu'):
    xml_corrige = xml.replace("xmlns=\"http://xml.sandre.eaufrance.fr/","xmlns:quesu=\"http://xml.sandre.eaufrance.fr/")

  return xml_corrige

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++







def main():

  parser = argparse.ArgumentParser(description="""
Ce script permet de lire les informations contenues dans un export SANDRE.
""", formatter_class=RawTextHelpFormatter)

  # mode debug optionnel pur sortie console
  global mode_debug
  if ('-debug' in sys.argv):
    mode_debug = True
    pass

  if ( len(sys.argv) == 1 ):
    # si on est là c'est que aucune commande n'a été demandée -> on affiche l'aide
    Logguer(parser.print_help())

  else:
    # le premier argument doit être le nom du fichier
    # TODO chemin relatif pour le moment
    f_sandre = ".\\" + sys.argv[1]

    # le 2e argument c'est le type de données
    # assai | quesu
    global type_donnees
    type_donnees = sys.argv[2]

    # nom du fichier de sortie
    global f_synthese
    f_synthese =  f_synthese +  str(sys.argv[1])[:-3] + "txt"

    # on prépare le fichie de sortie
    # w = on écrase le contenu existant
    with codecs.open(f_synthese, "w", "utf-8") as f:
      f.write("")
      f.close()

    Logguer("Extraction des informations du fichier SANDRE " + f_sandre)
    Logguer("")

    # on ouvre le fichier xml d'un coup
    xml_fichier = open(f_sandre,'r',encoding='utf-8').read()
    # on corrige le xml
    xml_corrige = CorrigerXmlSandre(xml_fichier)
    # on le force en utf-8 sinon on a des erreurs
    xml = xml_corrige.encode('utf-8')

    # on déclare la variable globale car le doc XML sera appelée dans les autres fonctions
    global xml_sandre_tree
    # enfin : on parse le xml
    xml_sandre_tree = etree.XML(xml)

    # les sous-fonctions
    ExtractionInfosGenerales()
    #ExtractionInfosMesures()

  pass

if __name__ == '__main__':
    main()
