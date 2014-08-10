## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.80.973 (20140810)                       ##
##                                                                            ##
##                                File: gui.py                                ##
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

# Import PyQt5 modules
from PyQt5.QtGui import (QPixmap, QPalette, QColor, QFont, QRegion,
                         QTransform, QFontDatabase)

# Import coub modules
import wdgt

#------------------------------------------------------------------------------#
# Module level constants
SMALL_PADDING = 5
LARGE_PADDING = 2*SMALL_PADDING


ICON_SIZE = 13
USER_SIZE = 38

POST_SHADOW_BLUR = 15
POST_SHADOW_OFFSET = 3

POST_SPACING_HEAD = int((POST_SHADOW_BLUR - POST_SHADOW_OFFSET) / 2)
POST_SPACING_TAIL = int((POST_SHADOW_BLUR + POST_SHADOW_OFFSET) / 2)
POST_ROUNDNESS = SMALL_PADDING

FOREGROUND = 0
BACKGROUND = 1

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
_SANS = 'Source Sans Pro'

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Global variable, holds all the static GUI informations
# It is initialised as empty because a QApplication has to
# run before any Q* object could be made or set
CONSTANTS = {}


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
_rgb = lambda s, a: QColor(*(int(_1+_2, 16) for _1, _2 in zip(*(iter(s+a),)*2)))

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def _image(file, rotate=None):
    pixmap = QPixmap(os_path_join('img', file))
    if rotate is None:
        return pixmap
    transform = QTransform()
    transform.rotate(rotate)
    return pixmap.transformed(transform)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def _palette(parent, place, string, alpha=100):
    palette = QPalette(parent)
    palette.setColor(QPalette.Background if place else QPalette.Foreground,
                     _rgb(string, '{:X}'.format(round(2.55 * alpha))))
    return palette

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def _color(string, alpha=100):
    return _rgb(string, '{:X}'.format(round(2.55 * alpha)))


#------------------------------------------------------------------------------#
# Create and set GUI constants
def set_gui_constants(parent):
    # TODO: after the design is settled, remove unnecessary font files
    weights = {'ExtraLight', 'Light', 'Semibold', 'Bold', 'Black'}
    weights ^= set(s + 'It' for s in copy(weights))
    weights ^= {'Regular', 'It'}
    # Load fonts
    fonts = QFontDatabase()
    for weight in weights:
        fonts.addApplicationFont('font/TTF/SourceSansPro-{}.ttf'.format(weight))

    # Palettes
    CONSTANTS['text_color_dark']    = _palette(parent, FOREGROUND, '000000', 45)
    CONSTANTS['text_color_light']   = _palette(parent, FOREGROUND, 'ffffff', 45)
    # CONSTANTS['panel_color_light']  = _palette(parent, BACKGROUND, '808080')
    CONSTANTS['panel_color_dark']   = _palette(parent, BACKGROUND, '282828')
    CONSTANTS['panel_color_darker'] = _palette(parent, BACKGROUND, '181818')

    # Colors
    CONSTANTS['shadow_color'] = _color('000000', 70)
    CONSTANTS['panel_color_light'] = _color('808080')

    DEBUG_ALPHA = 40
    CONSTANTS['debug1'] = _color('ffff00', DEBUG_ALPHA)
    CONSTANTS['debug2'] = _color('00ffff', DEBUG_ALPHA)
    CONSTANTS['debug3'] = _color('ff00ff', DEBUG_ALPHA)
    CONSTANTS['debug4'] = _color('ff0000', DEBUG_ALPHA)
    CONSTANTS['debug5'] = _color('00ff00', DEBUG_ALPHA)
    CONSTANTS['debug6'] = _color('0000ff', DEBUG_ALPHA)

    # Fonts
    CONSTANTS['text_font_title']   = QFont(_SANS, 16, QFont.Light)
    CONSTANTS['text_font_author']  = QFont(_SANS, 10, QFont.Normal, italic=True)
    CONSTANTS['text_font_numbers'] = QFont(_SANS, 12, QFont.Normal)
    CONSTANTS['text_font_generic'] = QFont(_SANS, 10, QFont.Normal)

    # Icons
    CONSTANTS['icon_no_avatar']   = _image('no_avatar.png')
    CONSTANTS['icon_scroll_up']   = _image('icons_scroll.png')
    CONSTANTS['icon_scroll_down'] = _image('icons_scroll.png', rotate=180)
    CONSTANTS['icon_recoub']      = _image('icons_share.png')
    CONSTANTS['icon_like']        = _image('icons_like.png')
    CONSTANTS['icon_featured']    = _image('icons_featured.png')
    CONSTANTS['icon_newest']      = _image('icons_newest.png')
    CONSTANTS['icon_random']      = _image('icons_random.png')
    CONSTANTS['icon_hot']         = _image('icons_hot.png')

    # Other images
    CONSTANTS['other_separator'] = _image('separator.png')

    # Animation
    CONSTANTS['anim_busy']     = os_path_join('img', 'loading.gif')
