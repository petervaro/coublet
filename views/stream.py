## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.172 (20140814)                       ##
##                                                                            ##
##                           File: views/stream.py                            ##
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
from PyQt5.QtWidgets import QWidget, QVBoxLayout

# Import coublet modules
from views.vars import *
from widgets.anim import CoubletAnimatedGifWidget

#------------------------------------------------------------------------------#
class CoubletStreamView(QVBoxLayout):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, presenter, parent=None):
        super().__init__(parent)
        # Store static values
        self._presenter = presenter
        # Build GUI
        self._build_gui()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def show_loading(self, sync):
        if sync:
            self.insertWidget(0, self._loading_indicator, alignment=Qt.AlignHCenter)
        else:
            self.addWidget(self._loading_indicator, alignment=Qt.AlignHCenter)
        self._loading_indicator.show()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def hide_loading(self):
        self._loading_indicator.hide()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def append_post(self, post):
        self.addWidget(post)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def insert_post(self, post):
        self.insertWidget(0, post)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _build_gui(self):
        # Set dimensional values
        self.setSpacing(POST_SPACING_HEAD + POST_SPACING_TAIL)
        self.setContentsMargins(LARGE_PADDING,
                                POST_SPACING_HEAD,
                                0,
                                POST_SPACING_TAIL)

        # Create loading indicator
        self._loading_indicator = CoubletAnimatedGifWidget(CONSTANTS['anim_busy_dark'], 32, 16)
        self._loading_indicator.hide()
