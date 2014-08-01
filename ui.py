## INFO ########################################################################
##                                                                            ##
##                                  COUB App                                  ##
##                                  ========                                  ##
##                                                                            ##
##      Cross-platform desktop application for following posts from COUB      ##
##                       Version: 0.5.50.090 (20140801)                       ##
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
                             QPushButton, QSizePolicy, QSlider, QStyle,
                             QVBoxLayout, QWidget, QDesktopWidget, QScrollArea)


#------------------------------------------------------------------------------#
class CoubPostUI(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, parent=None, file=None):
        super(CoubPostUI, self).__init__(parent)

        # TODO: likes, external link

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
        self.setFixedSize(320, 240)


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
        # TODO: make error label appear on the video itself
        #       test: CoubPost(parent, None) --> error loading media
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
class CoubStreamUI(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, parent=None):
        super(CoubStreamUI, self).__init__(parent)

        # Set layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def add_posts(self, *posts):
        print(posts)
        # Add new posts to stream
        for post in posts:
            self.layout.addWidget(CoubPostUI(self, post))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def clear(self):
        # Remove all posts from stream
        for i in reversed(range(self.layout.count())):
            # ??? setParent() or close() ???
            self.layout.itemAt(i).widget().setParent(None)



#------------------------------------------------------------------------------#
class CoubAppUI(QWidget):

    TITLE = 'COUB'
    MENU = 'featured', 'newest', 'random', 'user'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, root, x, y, width, height):
        super(CoubAppUI, self).__init__(None)
        self.root = root

        self.setWindowTitle(self.TITLE)

        self.layout = layout = QVBoxLayout()
        self.menu = menu = QHBoxLayout()
        self.posts = posts = QScrollArea()

        # Finalise layout
        layout.addWidget(posts)
        layout.addLayout(menu)
        self.setLayout(layout)

        self.streams = streams =[]
        for i, menu_item in enumerate(self.MENU):
            # Add menu item
            menu_button = QPushButton(menu_item)
            # b is needed because of the implementation `void triggered(bool = 0)`
            menu_button.clicked.connect(lambda b, n=i: self.on_menu_button_pressed(n))
            menu.addWidget(menu_button)
            # Add stream
            stream = CoubStreamUI(self)
            streams.append(stream)
            # stream.hide()

        # Set last stream selected
        self.stream = stream

        # Just for the sake of under-scored names ;)
        self.closeEvent = self.on_exit

        # If position have not been set before
        if x is NotImplemented:
            screen = QDesktopWidget().screenGeometry()
            x, y = (screen.width() - width) / 2, (screen.height() - height) / 2
        # Set window position and dimension
        self.setGeometry(x, y, width, height)

        # Load first stream
        self.on_menu_button_pressed(0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_exit(self, event):
        dim = self.frameGeometry()
        self.root.on_exit((dim.x(), dim.y()), (dim.width(), dim.height()))
        event.accept()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_menu_button_pressed(self, index):
        # Hide previous stream
        # self.stream.hide()
        self.stream = stream = self.streams[index]
        # stream.show()
        posts = self.posts
        posts.takeWidget()
        posts.setWidget(stream)
        posts.setWidgetResizable(True)
        stream.add_posts(*self.root.load_menu(index))
