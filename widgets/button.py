## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.172 (20140814)                       ##
##                                                                            ##
##                          File: widgets/button.py                           ##
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

# Import PyQt5 modules
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout

# Module level constants
ICON_AND_LABEL = 0
LABEL_AND_ICON = 1

VERTICAL   = 0
HORIZONTAL = 1

#------------------------------------------------------------------------------#
class CoubletButtonWidget(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # TODO: do something with width and height if provided
    def __init__(self, icon, label, order, orientation,
                 icon_selected=None, font=None, font_selected=None, palette=None,
                 palette_selected=None,
                 width=0, height=0, spacing=0, parent=None, mouse_event_handler=None,
                 padding_left=0, padding_top=0, padding_right=0, padding_bottom=0):
        super().__init__(parent)

        # Create layout
        layout = QHBoxLayout() if orientation else QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(padding_left, padding_top,
                                  padding_right, padding_bottom)
        # Set icon
        self._image = image = QLabel()
        image.setPixmap(icon)

        # If object has two stages
        if icon_selected:
            self._icon = icon
            self._icon_selected = icon_selected
        else:
            self._icon_selected = self._icon = icon

        # Set label
        text = QLabel(label)
        if font:
            text.setFont(font)
        if palette:
            text.setPalette(palette)

        if font_selected:
            self._text = text
            self._font = font
            self._font_selected = font_selected
        else:
            self._font_selected = self._font = font

        if palette_selected:
            self._text = text
            self._palette = palette
            self._palette_selected = palette_selected
        else:
            self._palette_selected = self._palette = palette

        # Place items in order
        for i, item in enumerate((image, text, image)[order:order+2]):
            if i:
                layout.addSpacing(spacing)
            layout.addWidget(item, alignment=Qt.AlignHCenter)

        # Set layout
        self.setLayout(layout)

        # Set mouse event if any
        if mouse_event_handler:
            self._event_handler = mouse_event_handler
            self.mouseReleaseEvent = self.on_mouse_release

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_mouse_release(self, event):
        self._event_handler.click(event.button())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def select(self):
        self._image.setPixmap(self._icon_selected)
        self._text.setFont(self._font_selected)
        self._text.setPalette(self._palette_selected)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def deselect(self):
        self._image.setPixmap(self._icon)
        self._text.setFont(self._font)
        self._text.setPalette(self._palette)
