## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.61.568 (20140805)                       ##
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
from os.path import join as os_path_join

# Import PyQt5 modules
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette, QColor, QFont, QRegion
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel,
                             QGraphicsDropShadowEffect)

# Import coub modules
import wdgt
from static import RESOURCES

#------------------------------------------------------------------------------#
# Module level constants
SMALL_PADDING = 5
LARGE_PADDING = 2*SMALL_PADDING

ICON_SIZE = 16

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
_image = lambda file: QPixmap(os_path_join('img', file))

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
    # Palettes
    CONSTANTS['text_color_dark']   = _color(parent, FOREGROUND, '000000', 45)
    CONSTANTS['text_color_light']  = _color(parent, FOREGROUND, 'ffffff', 60)
    CONSTANTS['panel_color_light'] = _color(parent, BACKGROUND, 'cccccc')
    CONSTANTS['panel_color_dark']  = _color(parent, BACKGROUND, '383838')

    # Colors
    # CONSTANTS['shadow_color'] = QColor(0x00, 0x00, 0x00, _alpha(70))

    # Fonts
    CONSTANTS['text_font_title']   = QFont(_SANS, 16, QFont.Light)
    CONSTANTS['text_font_author']  = QFont(_SANS, 10, QFont.Normal, italic=True)
    CONSTANTS['text_font_numbers'] = QFont(_SANS, 12, QFont.Normal)
    CONSTANTS['text_font_generic'] = QFont(_SANS, 10, QFont.Normal)

    # Icons
    CONSTANTS['icon_no_avatar']   = _image('no_avatar.png')
    CONSTANTS['icon_scroll_up']   = _image('scroll_up.png')
    CONSTANTS['icon_scroll_down'] = _image('scroll_down.png')
    CONSTANTS['icon_recoub']      = _image('recoub.png')
    CONSTANTS['icon_like']        = _image('like.png')
    CONSTANTS['icon_featured']    = _image('featured.png')
    CONSTANTS['icon_newest']      = _image('newest.png')
    CONSTANTS['icon_random']      = _image('random.png')
    CONSTANTS['icon_user']        = _image('user.png')

    # Animation
    # CONSTANTS['anim_spinner']     = _image('spinner.gif')



#------------------------------------------------------------------------------#
def build_post_style(widget, packet, video, thumb, width, height):
    # Create layout object for full post and zero-out
    main_layout = QVBoxLayout()
    main_layout.setSpacing(0)
    main_layout.setContentsMargins(*(0,)*4)

    # Create layout for content
    content_layout = QHBoxLayout()
    content_layout.setSpacing(0)
    content_layout.setContentsMargins(*(0,)*4)

    # Add video and thumb to content
    content_layout.addSpacing(SMALL_PADDING)
    content_layout.addWidget(video)
    content_layout.addWidget(thumb)
    content_layout.addSpacing(SMALL_PADDING)

    # Add layout to main layout
    main_layout.addSpacing(SMALL_PADDING)
    height += SMALL_PADDING
    main_layout.addLayout(content_layout)

    # Add padding, increase total height
    main_layout.addSpacing(SMALL_PADDING)
    height += SMALL_PADDING

    # Create layout object for info bar and zero-out
    info_layout = QHBoxLayout()
    info_layout.setSpacing(0)
    info_layout.setContentsMargins(*(0,)*4)

    # Create and add avatar
    avatar = QLabel()
    avatar_image = QPixmap(packet['user'][1])
    avatar.setPixmap(avatar_image)
    info_layout.addSpacing(SMALL_PADDING)
    info_layout.addWidget(avatar)

    # Create layout for text and zero-out
    text_layout = QVBoxLayout()
    text_layout.setSpacing(0)
    text_layout.setContentsMargins(*(0,)*4)

    # Create and add title
    # TODO: wrap title and author
    title = QLabel('“{}”'.format(packet['title']))
    title.setFont(CONSTANTS['text_font_title'])
    title.setPalette(CONSTANTS['text_color_dark'])
    text_layout.addWidget(title)

    # Create and add author
    author = QLabel('— {}'.format(packet['name']))
    author.setFont(CONSTANTS['text_font_author'])
    author.setPalette(CONSTANTS['text_color_dark'])
    text_layout.addWidget(author)

    # Add texts to the info bar
    info_layout.addSpacing(SMALL_PADDING)
    info_layout.addLayout(text_layout)

    # Create layout for social and zero-out
    social_layout = QVBoxLayout()
    social_layout.setSpacing(0)
    social_layout.setContentsMargins(*(0,)*4)

    # Create layout for like-counter and zero-out
    likes_layout = QHBoxLayout()
    likes_layout.setSpacing(0)
    likes_layout.setContentsMargins(*(0,)*4)

    # Create and add likes
    likes_icon = QLabel()
    likes_icon.setPixmap(CONSTANTS['icon_like'])

    likes_text = QLabel(packet['likes'])
    likes_text.setFont(CONSTANTS['text_font_numbers'])
    likes_text.setPalette(CONSTANTS['text_color_dark'])

    likes_layout.addSpacing(SMALL_PADDING)
    likes_layout.addWidget(likes_icon)
    likes_layout.addSpacing(SMALL_PADDING)
    likes_layout.addWidget(likes_text, alignment=Qt.AlignRight)

    # Create layout for share-counter and zero-out
    share_layout = QHBoxLayout()
    share_layout.setSpacing(0)
    share_layout.setContentsMargins(*(0,)*4)

    # Create and add shares
    share_icon = QLabel()
    share_icon.setPixmap(CONSTANTS['icon_recoub'])

    share_text = QLabel(packet['share'])
    share_text.setFont(CONSTANTS['text_font_numbers'])
    share_text.setPalette(CONSTANTS['text_color_dark'])

    share_layout.addSpacing(SMALL_PADDING)
    share_layout.addWidget(share_icon)
    share_layout.addSpacing(SMALL_PADDING)
    share_layout.addWidget(share_text, alignment=Qt.AlignRight)

    # Add likes and share to social
    social_layout.addLayout(likes_layout)
    social_layout.addLayout(share_layout)

    # Add social to the info bar
    info_layout.addStretch(0)
    info_layout.addLayout(social_layout)
    info_layout.addSpacing(SMALL_PADDING)

    # Add info, increase total height
    main_layout.addLayout(info_layout)
    height += avatar_image.height()

    # Add bottom padding
    main_layout.addSpacing(SMALL_PADDING)
    height += SMALL_PADDING

    # Set layout for this widget
    widget.setLayout(main_layout)

    # Set color of this widget
    widget.setAutoFillBackground(True)
    widget.setPalette(CONSTANTS['panel_color_light'])


    # Set size and load content
    widget.setFixedSize(width + 2*SMALL_PADDING, height)

    # Make it rounded
    _rounded_rectangle(widget, *(SMALL_PADDING,)*4)

    # FIXME: DropShadow has a "funny" effect on the post,
    #        because of that the full info-bar scrolls away
    #        after the video started playing

    # # Add drop shadow to this widget
    # shadow = QGraphicsDropShadowEffect(widget)
    # shadow.setColor(CONSTANTS['shadow_color'])
    # shadow.setBlurRadius(15)
    # shadow.setOffset(0, 3)
    # widget.setGraphicsEffect(shadow)



#------------------------------------------------------------------------------#
def build_stream_style(widget):
    # Create layout
    widget.layout = layout = QVBoxLayout()
    layout.setSpacing(0)
    layout.setContentsMargins(LARGE_PADDING, 0, 0, 0)

    # Add animated spinner
    widget.spinner = wdgt.AnimatedGif(file=RESOURCES['spinner'],
                                      width=20,
                                      height=20,
                                      padding_x=LARGE_PADDING,
                                      padding_y=LARGE_PADDING)
    # Add scroll-up icon and text
    layout.addWidget(wdgt.IconLabel(icon=CONSTANTS['icon_scroll_up'],
                                    label='SCROLL UP TO REFRESH',
                                    font=CONSTANTS['text_font_generic'],
                                    palette=CONSTANTS['text_color_light'],
                                    order=wdgt.LABEL_AND_ICON,
                                    orientation=wdgt.VERTICAL,
                                    width=10,
                                    height=10,
                                    padding_x=LARGE_PADDING,
                                    padding_y=LARGE_PADDING))
    # Add scroll-down icon and text
    layout.addStretch(0)
    layout.addWidget(wdgt.IconLabel(icon=CONSTANTS['icon_scroll_down'],
                                    label='SCROLL DOWN TO LOAD MORE',
                                    font=CONSTANTS['text_font_generic'],
                                    palette=CONSTANTS['text_color_light'],
                                    order=wdgt.ICON_AND_LABEL,
                                    orientation=wdgt.VERTICAL,
                                    width=10,
                                    height=10,
                                    padding_x=LARGE_PADDING,
                                    padding_y=LARGE_PADDING))
    # Set layout
    widget.setLayout(layout)



#------------------------------------------------------------------------------#
def build_app_style(widget):

    widget.setPalette(CONSTANTS['panel_color_dark'])
