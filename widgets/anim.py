## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.066 (20140813)                       ##
##                                                                            ##
##                           File: widgets/anim.py                            ##
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

# IMport Python modules
from random import random

# Import PyQt5 modules
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QByteArray
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout

#------------------------------------------------------------------------------#
class CoubletAnimatedGifWidget(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, file, width, height, padding_x=0, padding_y=0, parent=None):
        super().__init__(parent)

        self.setFixedSize(width + 2*padding_x, height + 2*padding_y)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(*(padding_x, padding_y)*2)

        label = QLabel()
        label.setFixedSize(width, height)

        self._movie = movie = QMovie(file, QByteArray(), self)
        movie.setCacheMode(QMovie.CacheAll)
        movie.setSpeed(120)
        movie.start()

        label.setMovie(movie)
        layout.addWidget(label)

        self.setLayout(layout)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def random_frame(self):
        # Jump to a random frame
        self._movie.jumpToFrame(int(random() * self._movie.frameCount()))
