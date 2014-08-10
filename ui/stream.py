## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.80.980 (20140810)                       ##
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
from .post import CoubPostUI

#------------------------------------------------------------------------------#
class CoubStreamUI(QVBoxLayout):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, index, parent=None):
        super().__init__(parent)

        # Store static values
        self.index = index
        self.visited = False

        # Storage of posts for faster iteration
        self._posts = set()

        # Set GUI values
        self.setSpacing(gui.POST_SPACING_HEAD + gui.POST_SPACING_TAIL)
        self.setContentsMargins(gui.LARGE_PADDING,
                                gui.POST_SPACING_HEAD,
                                0,
                                gui.POST_SPACING_TAIL)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def add_posts(self, count):
        # Get local reference
        posts  = self._posts
        # Store start index
        self._post_index = self.count()
        # Add empty posts
        for i in range(count):
            post = CoubPostUI()
            posts.add(post)
            self.addWidget(post)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load_post(self, post):
        # Get index and coublet-packet
        index, packet = post
        # Load content into the previously created CoubPostUI widget
        self.itemAt(self._post_index + index).widget().load(packet)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def reset_unseen_posts(self):
        # Iterate through all posts
        for post in self._posts:
            # And if post is not visible
            # (not rendered) and not playing
            if post.visibleRegion().isEmpty():
                # Reset that post
                post.kill()
