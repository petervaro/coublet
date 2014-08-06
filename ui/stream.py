## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.70.703 (20140806)                       ##
##                                                                            ##
##                             File: ui/stream.py                             ##
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
import gui
import wdgt
from ui.post import CoubPostUI

#------------------------------------------------------------------------------#
class CoubStreamUI(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, index, parent=None):
        super().__init__(parent)

        # Store static values
        # ??? Do we need this index value ???
        self.index = index
        self.visited = False
        # Build UI
        self._build_gui()
        # Initially hide spinner
        self.spinner.hide()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def add_slots(self, count):
        layout = self.layout
        # Insert before space
        self._post_index = post_index = layout.count() - 2
        for i in range(count):
            layout.insertWidget(post_index, QWidget())#, alignment=Qt.AlignTop)
            # layout.insertSpacing(post_index, gui.POST_SPACING)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def add_post(self, post):
        layout = self.layout
        index, packet = post
        post_index = self._post_index + index + 1
        # Remove slot
        # layout.itemAt(post_index).widget().hide()
        # Add widget and tail padding
        # layout.insertWidget(post_index, CoubPostUI(packet), alignment=Qt.AlignTop)
        layout.replaceWidget(layout.itemAt(post_index).widget(),
                             CoubPostUI(packet))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def spin(self, reload=False):
        # Insert before space
        length = self.layout.count()
        self.layout.insertWidget(1 if length == 1 or reload else length - 2,
                                 self.spinner,
                                 alignment=Qt.AlignHCenter)
        self.spinner.show()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def spin_off(self):
        # Turn off indication of loading
        self.spinner.hide()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def clear(self):
        # Remove all posts from stream
        for i in reversed(range(self.layout.count())):
            # ??? setParent() or close() ???
            self.layout.itemAt(i).widget().setParent(None)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _build_gui(self):
        # Create layout
        self.layout = layout = QVBoxLayout()
        layout.setSpacing(gui.POST_SPACING)
        layout.setContentsMargins(gui.LARGE_PADDING, 0, 0, 0)

        # Add animated spinner
        self.spinner = wdgt.AnimatedGif(file=gui.CONSTANTS['anim_spinner'],
                                          width=20,
                                          height=20,
                                          padding_x=gui.LARGE_PADDING,
                                          padding_y=gui.LARGE_PADDING)
        # Add scroll-up icon and text
        layout.addWidget(wdgt.IconLabel(icon=gui.CONSTANTS['icon_scroll_up'],
                                        label='SCROLL UP TO REFRESH',
                                        font=gui.CONSTANTS['text_font_generic'],
                                        palette=gui.CONSTANTS['text_color_light'],
                                        order=wdgt.ICON_AND_LABEL,
                                        orientation=wdgt.VERTICAL,
                                        spacing=gui.SMALL_PADDING,
                                        padding_x=gui.LARGE_PADDING,
                                        padding_y=gui.LARGE_PADDING))
        # Add scroll-down icon and text
        layout.addStretch(0)
        layout.addWidget(wdgt.IconLabel(icon=gui.CONSTANTS['icon_scroll_down'],
                                        label='SCROLL DOWN TO LOAD MORE',
                                        font=gui.CONSTANTS['text_font_generic'],
                                        palette=gui.CONSTANTS['text_color_light'],
                                        order=wdgt.LABEL_AND_ICON,
                                        orientation=wdgt.VERTICAL,
                                        spacing=gui.SMALL_PADDING,
                                        padding_x=gui.LARGE_PADDING,
                                        padding_y=gui.LARGE_PADDING))
        # Set layout
        self.setLayout(layout)
