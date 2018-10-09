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
# pour une station : pas d'API
#  http://www.sandre.eaufrance.fr/urn.php?urn=urn:sandre:donnees:SysTraitementEauxUsees:FRA:code:0435047S0003:::::xml
# pour obtenir le nom des paramètres
# https://api.sandre.eaufrance.fr/referentiels/v1/parametre.xml?filter=<Filter><IS><Field>CdParametre</Field><Value>1313</Value></IS></Filter>

# problème dans le fichier SANDRE : le namespace n'a pas de prefixe
# ligne 4 = rajout à la main
# xmlns:assai="http://xml.sandre.eaufrance.fr/scenario/fct_assain/3"


import os, sys
import argparse
from argparse import RawTextHelpFormatter
import configparser
from lxml import etree
import codecs
import pprint


# répertoire courant
script_dir = os.path.dirname(__file__)

# lecture du fichier de configuration
config = configparser.ConfigParser()
config.read( script_dir + '/config.ini')

# fichier de sortie
f_synthese = script_dir + "\\synthese_"

# variables globales
mode_debug = False


# xml namespaces
cfg = {
  'ns': {
    'assai'   : u'http://xml.sandre.eaufrance.fr/scenario/fct_assain/3'
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

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def xmlGetTextNodes(doc, xpath):
    """
    shorthand to retrieve serialized text nodes matching a specific xpath
    """
    return '|'.join(doc.xpath(xpath, namespaces=cfg['ns']))

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def ExtractionInfosGenerales():

  Logguer("Extraction des infos générales sur le fichier")

  # ce que contient le fichier
  Scenario = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/Scenario/NomScenario/text()')
  # plage de dates des données
  DateDebutReference = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/Scenario/DateDebutReference/text()')
  DateFinReference = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/Scenario/DateFinReference/text()')

  # on écrit dans le fichier
  with codecs.open(f_synthese, "a", "utf-8") as f:
    f.write("Scénario : " + Scenario + "\n")
    f.write("date de début des données : " + DateDebutReference + "\n")
    f.write("date de fin des données   : " + DateFinReference + "\n")
    f.write("\n")
    f.close()

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
    with codecs.open(f_synthese, "a", "utf-8") as f:
      f.write("code SANDRE de la station : " + CdOuvrageDepollution + "\n")
      f.write("Nom de la station dans le fichier : " + NomOuvrageDepollution + "\n")
      f.write("Détails de la station dans le SI Eau  : " + DetailXMLStation + "\n")
      f.write("\n")
      f.close()

  Logguer("fait")
  Logguer("")


 # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def ExtractionInfosMesures():

  Logguer("Extraction des infos sur les mesures et les paramètres")

  # on compte le nb de PointMesure
  nbPointMesure = len( xml_sandre_tree.xpath('/FctAssain/OuvrageDepollution/PointMesure', namespaces=cfg['ns']) )

  Logguer( str(nbPointMesure) + " point(s) de mesure trouvé(s)" )
  with codecs.open(f_synthese, "a", "utf-8") as f:
    f.write(str(nbPointMesure) + " point(s) de mesure trouvé(s)" + "\n")
    f.write("\n")
    f.close()

  # boucle sur les points de mesure
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
    while idxPrlvt <= nbPrlvt :
      # nb d'analyses
      nbAnalyses = len( xml_sandre_tree.xpath('/FctAssain/OuvrageDepollution/PointMesure['+str(idxMesure)+']/Prlvt['+str(idxPrlvt)+']/Analyse', namespaces=cfg['ns']) )
      Logguer( "    " + str(nbAnalyses) + " analyses trouvées" )

      # boucle sur les analyses
      idxAnalyse = 1
      while idxAnalyse <= nbAnalyses :
        CdParametre = xmlGetTextNodes(xml_sandre_tree, '/FctAssain/OuvrageDepollution/PointMesure['+str(idxMesure)+']/Prlvt['+str(idxPrlvt)+']/Analyse['+str(idxAnalyse)+']/Parametre/CdParametre/text()')
        Logguer( "      paramètre trouvé : " + str(CdParametre) )

        idxAnalyse += 1

      idxPrlvt += 1

    idxMesure += 1



  Logguer("")
  Logguer("------------------------------------------------------------")
  Logguer("")

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

    Logguer("Traitement du fichier : " + f_sandre)
    Logguer("")
    # nom du fichier de sortie
    global f_synthese
    f_synthese =  f_synthese +  str(sys.argv[1])[:-3] + "txt"


    # on ouvre le fichier
    global xml_sandre_tree
    xml_sandre_tree = etree.parse( f_sandre )

    # on prépare le fichie de sortie
    # w = on écrase le contenu existant
    with codecs.open(f_synthese, "w", "utf-8") as f:
      f.write("Extraction des informations du fichier SANDRE " + f_sandre + "\n")
      f.write("\n")
      f.close()

    ExtractionInfosGenerales()
    ExtractionInfosMesures()




  pass

if __name__ == '__main__':
    main()
