# coding: utf8
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
# pour obtenir le nom des paramètres

# problème dans le fichier SANDRE : le namespace n'a pas de prefixe
# ligne 4 = rajout à la main
# xmlns:assai="http://xml.sandre.eaufrance.fr/scenario/fct_assain/3"


import os, sys
import argparse
from argparse import RawTextHelpFormatter
import configparser
from lxml import etree


# répertoire courant
script_dir = os.path.dirname(__file__)

# lecture du fichier de configuration
config = configparser.ConfigParser()
config.read( script_dir + '/config.ini')


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


def ExtractionScenario():

  Logguer("Extraction des infos du scénario")

  print( xmlGetTextNodes(xml_sandre_tree, '/FctAssain/Scenario/NomScenario/text()')  )



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
    f_sandre = ".\\" + sys.argv[1]

    Logguer("Traitement du fichier : " + f_sandre)


    # on ouvre le fichier
    global xml_sandre_tree
    xml_sandre_tree = etree.parse( f_sandre )

    ExtractionScenario()




  pass

if __name__ == '__main__':
    main()
