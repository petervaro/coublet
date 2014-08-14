## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.172 (20140814)                       ##
##                                                                            ##
##                               File: setup.py                               ##
##                                                                            ##
##           Designed and written by Peter Varo. Copyright (c) 2014           ##
##             License agreement is provided in the LICENSE file              ##
##           For more info visit: https://github.com/petervaro/coub           ##
##                                                                            ##
##      Copyright (c) 2014 Coub Ltd and/or its suppliers and licensors,       ##
##    5 Themistokli Dervi Street, Elenion Building, 1066 Nicosia, Cyprus.     ##
##         All rights reserved. COUB (TM) is a trademark of Coub Ltd.         ##
##                              http://coub.com                               ##
##                                                                            ##
######################################################################## INFO ##

# build:
#     python3 setup.py py2app
# clean up:
#     rm -rf build dist

# from os.path import join, splitext
# from setuptools import setup

# APP = ['main.py']
# DATA_FILES = []
# OPTIONS = {'argv_emulation': True,
#            'iconfile': 'img/coublet.icns',
#            'includes': ['sip',
#                         'PyQt5',
#                         'PyQt5.QtCore',
#                         'PyQt5.QtGui',
#                         'PyQt5.QtWidgets',
#                         'PyQt5.MultimediaWidgets',
#                         'PyQt5.Multimedia',
#                         'PyQt5.QtNetwork'],}

# setup(app=APP,
#       data_files=DATA_FILES,
#       options={'py2app': OPTIONS},
#       setup_requires=['py2app'],)

# # HACK: based on http://stackoverflow.com/questions/11068486
# with open(join('dist', splitext(APP[0])[0] + '.app', 'Contents', 'Resources', 'qt.conf'), 'w'):
#     pass

import sys
from os.path import join
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

OPTIONS = {'build_exe':{'includes': ['sip',
                                     'PyQt5',
                                     'PyQt5.QtCore',
                                     'PyQt5.QtGui',
                                     'PyQt5.QtWidgets',
                                     'PyQt5.QtMultimediaWidgets',
                                     'PyQt5.QtMultimedia',
                                     'PyQt5.QtNetwork']}}

EXECUTABLES = [Executable('main.py', base=base)]

NAME = 'coublet'
VERSION = '0.5.70'

setup(name = NAME,
      version = VERSION,
      options = OPTIONS,
      executables = EXECUTABLES)
