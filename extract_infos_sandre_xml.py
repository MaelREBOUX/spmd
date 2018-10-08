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

import os, sys
import argparse
from argparse import RawTextHelpFormatter
import configparser


# répertoire courant
script_dir = os.path.dirname(__file__)

# lecture du fichier de configuration
config = configparser.ConfigParser()
config.read( script_dir + '/config.ini')


# variables globales
mode_debug = False





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








def main():

  parser = argparse.ArgumentParser(description="""
Ce script permet de lire les informations contenues dans un export SANDRE.
""", formatter_class=RawTextHelpFormatter)

  # mode debug optionnel pur sortie console
  if ('-debug' in sys.argv):
    mode_debug = True
    ArgvIdEnquete = ArgvIdEnquete + 1
    pass

  # si on est là c'est que aucune commande n'a été demandée -> on affiche l'aide
  Logguer(parser.print_help())

  pass

if __name__ == '__main__':
    main()
