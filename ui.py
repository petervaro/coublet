## INFO ########################################################################
##                                                                            ##
##                                  COUB App                                  ##
##                                  ========                                  ##
##                                                                            ##
##      Cross-platform desktop application for following posts from COUB      ##
##                       Version: 0.5.50.015 (20140731)                       ##
##                                                                            ##
##                File: /Users/petervaro/Documents/coub/ui.py                 ##
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

# Import Python modules
import os

# Import PyQt5 modules
from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)


#------------------------------------------------------------------------------#
class CoubPostUI(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, parent=None, file=None):
        super(CoubPostUI, self).__init__(parent)

        # Flags
        self._post = True
        self._mute = False
        self._loop = False

        # Media player
        self.player = player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        # Video Area
        video = QVideoWidget()

        # Set area, and event handlers of media player
        player.setVideoOutput(video)
        player.stateChanged.connect(self.on_state_changed)
        player.error.connect(self.on_error)
        player.setMedia(QMediaContent(QUrl.fromLocalFile(file)))

        # Set error label
        self.error_label = error_label = QLabel()
        error_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Build layout
        layout = QVBoxLayout()
        layout.addWidget(video)
        layout.addWidget(error_label)
        self.setLayout(layout)

        # Just for the sake of under-scored names ;)
        self.mousePressEvent = self.on_mouse_pressed

        # Set size and load content
        self.resize(320, 240)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_mouse_pressed(self, event):
        if event.button() == Qt.LeftButton:
            self.play()
        if event.button() == Qt.RightButton:
            self.mute()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_state_changed(self, state):
        # If looping
        if self._loop:
            self.player.play()
        # If paused
        else:
            # Continue looping
            self._loop = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_error(self):
        self._post = False
        self.error_label.setText('ERROR: ' + self.player.errorString())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def mute(self):
        # If post is not valid
        if not self._post:
            return
        # If already muted
        elif self._mute:
            self._mute = False
            self.player.setVolume(100)
        # If needs to be muted
        else:
            self._mute = True
            self.player.setVolume(0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def play(self):
        # If post is not valid
        if not self._post:
            return
        # If playing
        elif self.player.state() == QMediaPlayer.PlayingState:
            # Stop playing the loop
            self._loop = False
            self.player.pause()
        # If paused
        else:
            # Start playing the loop
            self._loop = True
            self.player.play()


#------------------------------------------------------------------------------#
class CoubAppUI(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, root, parent=None):
        super(CoubAppUI, self).__init__(parent)
        self.root = root

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Just for the sake of under-scored names ;)
        self.closeEvent = self.on_exit

        # Set default size
        # TODO: Store size in cache folder
        self.resize(320, 768)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_exit(self, event):
        self.root.on_exit()
        event.accept()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def append(self, *files):
        # Create post for each file
        for file in files:
            post = CoubPostUI(self, file)
            self.layout.addWidget(post)
