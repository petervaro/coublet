## INFO ########################################################################
##                                                                            ##
##                                  COUB App                                  ##
##                                  ========                                  ##
##                                                                            ##
##      Cross-platform desktop application for following posts from COUB      ##
##                       Version: 0.5.61.430 (20140804)                       ##
##                                                                            ##
##                              File: static.py                               ##
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

# Import python modules
from copy import copy
from os.path import join as os_path_join

#------------------------------------------------------------------------------#
_img_path = lambda file: os_path_join('img', file)

#------------------------------------------------------------------------------#
# TODO: Add SVG support to icons
RESOURCES = {'no_avatar'  : _img_path('no_avatar.png'),
             'spinner'    : _img_path('spinner.gif'),
             'scroll_up'  : _img_path('scroll_up.png'),
             'scroll_down': _img_path('scroll_down.png'),
             'recoub'     : _img_path('recoub.png'),
             'like'       : _img_path('like.png')}

#------------------------------------------------------------------------------#
# Font FONTS
# TODO: after the design is settled, remove unnecessary font files
FONTS = {'ExtraLight', 'Light', 'Semibold', 'Bold', 'Black'}
FONTS ^= set(s + 'It' for s in copy(FONTS))
FONTS ^= {'Regular', 'It'}
