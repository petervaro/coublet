## INFO ########################################################################
##                                                                            ##
##                                  COUB App                                  ##
##                                  ========                                  ##
##                                                                            ##
##      Cross-platform desktop application for following posts from COUB      ##
##                       Version: 0.5.61.186 (20140802)                       ##
##                                                                            ##
##                                File: ui.py                                 ##
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
import queue

# Import PyQt5 modules
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QDir, Qt, QUrl, QTimer, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle,
                             QVBoxLayout, QWidget, QDesktopWidget, QScrollArea)


#------------------------------------------------------------------------------#
class CoubPostUI(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, parent=None, packet=None):
        super(CoubPostUI, self).__init__(parent)

        # Get proper dimensions
        width = 320
        height = int(width * packet['ratio'])

        # TODO: likes, external link

        # Flags
        self._post = True
        self._mute = False
        self._loop = False

        # Preview
        thumb = QPixmap(packet['thumb'][1])

        self.image = image = QLabel(self)
        image.setPixmap(thumb.scaled(width, height))

        # Media player
        self.player = player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        # Video Area
        self.video = video = QVideoWidget(self)

        # Set area, and event handlers of media player
        player.setVideoOutput(video)
        player.stateChanged.connect(self.on_state_changed)
        player.error.connect(self.on_error)
        player.setMedia(QMediaContent(QUrl.fromLocalFile(packet['video'][1])))

        # Set error label
        self.error_label = error_label = QLabel()
        error_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Build layout
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(video)
        layout.addWidget(image)
        layout.addWidget(error_label)
        self.setLayout(layout)

        video.hide()
        error_label.hide()

        # Just for the sake of under-scored names ;)
        self.mousePressEvent = self.on_mouse_pressed

        # Set size and load content
        self.setFixedSize(width, height)


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
        self.error_label.show()
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
            self.image.hide()
            self.video.show()
            self.player.play()



#------------------------------------------------------------------------------#
class CoubStreamUI(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, parent=None):
        super(CoubStreamUI, self).__init__(parent)

        # Set layout
        self.layout = layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def add_posts(self, *packets):
        # Add new posts to stream
        for packet in packets:
            self.layout.addWidget(CoubPostUI(self, packet))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def clear(self):
        # Remove all posts from stream
        for i in reversed(range(self.layout.count())):
            # ??? setParent() or close() ???
            self.layout.itemAt(i).widget().setParent(None)



#------------------------------------------------------------------------------#
class CoubAppUI(QWidget):

    TITLE = 'COUB'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, root, x, y, width, height, menu_labels):
        super(CoubAppUI, self).__init__(None)
        self.root = root
        self.menu_labels = menu_labels

        self.setWindowTitle(self.TITLE)

        self.layout = layout = QVBoxLayout()
        self.menu = menu = QHBoxLayout()
        self.posts = posts = QScrollArea()
        posts.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        posts.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        posts.verticalScrollBar().valueChanged.connect(self._on_update_stream)

        # Finalise layout
        menu.setSpacing(0)
        menu.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(posts)
        layout.addLayout(menu)
        self.setLayout(layout)

        self.streams = streams = []
        self._packets = packets = []
        for i, menu_item in enumerate(self.menu_labels):
            # Add menu item
            menu_button = QPushButton(menu_item)
            # b is needed because of the implementation `void triggered(bool = 0)`
            menu_button.clicked.connect(lambda b, n=i: self.on_menu_button_pressed(n))
            menu.addWidget(menu_button)
            # Add stream
            stream = CoubStreamUI(self)
            streams.append(stream)
            # Add stream specific packet queue
            packets.append(queue.Queue())

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
        self.setMaximumWidth(width)

        # Load first stream
        self.on_menu_button_pressed(0)
        # Start checking if Queue has items
        self.on_load_posts(0)

    # Scrolling related stuffs:
    #
    # self.posts.verticalScrollBar().value()      # getter
    # self.posts.verticalScrollBar().setValue()   # setter
    #
    # Consider using QListWidget instead of QScrollArea
    # more info: http://qt-project.org/doc/qt-4.8/qlistwidget.html

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_exit(self, event):
        dim = self.frameGeometry()
        self.root.on_exit((dim.x(), dim.y()), (dim.width(), dim.height()))
        event.accept()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_load_posts(self, index):
        try:
            # Load as many posts as possible
            while True:
                self.stream.add_posts(self._packets[index].get_nowait())
        except queue.Empty:
            pass
        finally:
            # Start loading posts again later
            QTimer.singleShot(500, lambda i=index: self.on_load_posts(index))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _on_update_stream(self, value):
        # TODO: check if there is an on-going update
        if value and value == self.posts.verticalScrollBar().maximum():
            print('[SCROLL] {} / {}'.format(value, self.posts.verticalScrollBar().maximum()))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_menu_button_pressed(self, index):
        # Set selected stream
        self.stream = self.streams[index]
        # Remove previously selected stream
        posts = self.posts
        posts.takeWidget()
        # Indicate change in window title
        self.setWindowTitle('{} | {}'.format(self.TITLE,
                                             self.menu_labels[index].upper()))
        # And set new stream
        posts.setWidget(self.stream)
        posts.setWidgetResizable(True)
        # Load data
        self.root.load_menu(index, self._packets[index])
