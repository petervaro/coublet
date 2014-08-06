## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.70.668 (20140806)                       ##
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

POST_SPACING = 15

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

def _image(file, rotate=None):
    pixmap = QPixmap(os_path_join('img', file))
    if rotate is None:
        return pixmap
    transform = QTransform()
    transform.rotate(rotate)
    return pixmap.transformed(transform)

def _color(parent, place, string, alpha=100):
    alpha = '{:X}'.format(round(2.55 * alpha))
    palette = QPalette(parent)
    palette.setColor(QPalette.Background if place else QPalette.Foreground,
                     QColor(*(int(a+b, 16) for a, b in zip(*(iter(string + alpha),)*2))))
    return palette


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def _rounded_rectangle(widget, tl, tr, br, bl):

    # FIXME: the mask produced by this function
    #        does not have antialiased edges

    width  = widget.width()
    height = widget.height()

    # A rectangle identical to the widget
    region = QRegion(0, 0, width, height, QRegion.Rectangle)

    # Set top-left corner
    radius = QRegion(0, 0, 2*tl, 2*tl, QRegion.Ellipse)
    corner = QRegion(0, 0, tl, tl, QRegion.Rectangle)
    region = region.subtracted(corner.subtracted(radius))

    # Set top-right corner
    radius = QRegion(width - 2*tr, 0, 2*tr, 2*tr, QRegion.Ellipse)
    corner = QRegion(width - tr, 0, tr, tr, QRegion.Rectangle)
    region = region.subtracted(corner.subtracted(radius))

    # Set bottom-right corner
    radius = QRegion(width - 2*br, height - 2*br, 2*br, 2*br, QRegion.Ellipse)
    corner = QRegion(width - br, height - br, br, br, QRegion.Rectangle)
    region = region.subtracted(corner.subtracted(radius))

    # Set bottom-left corner
    radius = QRegion(0, height - 2*bl, 2*bl, 2*bl, QRegion.Ellipse)
    corner = QRegion(0, height - bl, bl, bl, QRegion.Rectangle)
    region = region.subtracted(corner.subtracted(radius))

    # Mask widget
    widget.setMask(region)



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
    CONSTANTS['text_color_dark']    = _color(parent, FOREGROUND, '000000', 45)
    CONSTANTS['text_color_light']   = _color(parent, FOREGROUND, 'ffffff', 45)
    CONSTANTS['panel_color_light']  = _color(parent, BACKGROUND, '808080')
    CONSTANTS['panel_color_dark']   = _color(parent, BACKGROUND, '282828')
    CONSTANTS['panel_color_darker'] = _color(parent, BACKGROUND, '181818')

    # Colors
    # CONSTANTS['shadow_color'] = QColor(0x00, 0x00, 0x00, _alpha(70))

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
    CONSTANTS['anim_spinner']     = os_path_join('img', 'spinner.gif')
