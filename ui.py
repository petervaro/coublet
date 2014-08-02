## INFO ########################################################################
##                                                                            ##
##                                  COUB App                                  ##
##                                  ========                                  ##
##                                                                            ##
##      Cross-platform desktop application for following posts from COUB      ##
##                       Version: 0.5.61.294 (20140803)                       ##
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
import webbrowser

# Import PyQt5 modules
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QDir, Qt, QUrl, QTimer, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle,
                             QVBoxLayout, QWidget, QDesktopWidget, QScrollArea)

# Import coub modules
import wdgt

#------------------------------------------------------------------------------#
class CoubPostUI(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, parent=None, packet=None):
        super().__init__(parent)

        # Get proper dimensions
        width = 320
        height = int(width * packet['ratio'])

        # TODO: likes, external link

        # Flags
        self._post = True
        self._mute = False
        self._audio_loop = False
        self._video_loop = False

        self._link = packet['perma']



        #   CHECK WHY IS THERE TWO SPINNERS
        #   CONNECT SCROLLING UPDATE AND RELOAD



        # Preview
        thumb = QPixmap(packet['thumb'][1])

        self.image = image = QLabel(self)
        image.setPixmap(thumb.scaled(width, height))

        # Media players
        self.video_player = video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        # Video Area
        self.video = video = QVideoWidget(self)
        audio = packet['audio']
        if audio:
            self.audio_player = audio_player = QMediaPlayer(None)
            audio_player.stateChanged.connect(self.on_audio_state_changed)
            audio_player.error.connect(self.on_error)
            audio_player.setMedia(QMediaContent(QUrl(audio)))

        # Set area, and event handlers of media video_player
        video_player.setVideoOutput(video)
        video_player.stateChanged.connect(self.on_video_state_changed)
        video_player.error.connect(self.on_error)
        video_player.setMedia(QMediaContent(QUrl.fromLocalFile(packet['video'][1])))

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
        self.mouseReleaseEvent = self.on_mouse_release

        # Set mouse events
        interval = QApplication.instance().doubleClickInterval()
        self._clicker = wdgt.MouseClick(interval,
                                        l_single=self.play,
                                        l_double=self.open,
                                        r_single=self.mute)

        # Set size and load content
        self.setFixedSize(width, height)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_mouse_release(self, event):
        self._clicker.click(event.button())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def open(self):
        # Stop playing
        self._audio_loop = False
        self._video_loop = False
        self.video_player.pause()
        try:
            self.audio_player.pause()
        except AttributeError:
            pass
        # Open in browser
        webbrowser.open_new_tab(self._link)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_audio_state_changed(self, event):
        # If looping
        if self._audio_loop:
            self.audio_player.play()
        # If paused
        else:
            # Reset looping
            self._audio_loop = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_video_state_changed(self, state):
        # If looping
        if self._video_loop:
            self.video_player.play()
        # If paused
        else:
            # Reset looping
            self._video_loop = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_error(self):
        # TODO: make error label appear on the video itself
        #       test: CoubPost(parent, None) --> error loading media
        self._post = False
        self.error_label.show()
        self.error_label.setText('ERROR: ' + self.video_player.errorString())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def mute(self):
        # If post is not valid
        if not self._post:
            return
        # If already muted
        elif self._mute:
            self._mute = False
            self.video_player.setVolume(100)
            try:
                self.audio_player.setVolume(100)
            except AttributeError:
                pass
        # If needs to be muted
        else:
            self._mute = True
            self.video_player.setVolume(0)
            try:
                self.audio_player.setVolume(0)
            except AttributeError:
                pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def play(self):
        # If post is not valid
        if not self._post:
            return
        # If playing
        elif self.video_player.state() == QMediaPlayer.PlayingState:
            # Stop playing the loop
            self._audio_loop = False
            self._video_loop = False
            self.video_player.pause()
            try:
                self.audio_player.pause()
            except AttributeError:
                pass
        # If paused
        else:
            # Start playing the loop
            self._audio_loop = True
            self._video_loop = True
            self.image.hide()
            self.video.show()
            self.video_player.play()
            try:
                self.audio_player.play()
            except AttributeError:
                pass



#------------------------------------------------------------------------------#
class CoubStreamUI(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set layout
        self.layout = layout = QVBoxLayout()

        self.spinner = wdgt.AnimatedGif(os.path.join('img', 'spinner.gif'))
        self.spinner.setAlignment(Qt.AlignHCenter)
        self.spinner.setMargin(10)
        self.spinner.hide()

        layout.setSpacing(0)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addStretch(0)
        self.setLayout(layout)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def add_posts(self, *packets):
        # Add new posts to stream
        layout = self.layout
        self.spinner.hide()
        for packet in packets:
            # Insert before space
            layout.insertWidget(layout.count() - 2,
                                CoubPostUI(self, packet),
                                alignment=Qt.AlignTop)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def spin(self):
        # Insert before space
        length = self.layout.count()
        self.layout.insertWidget(0 if length == 1 else length - 2,
                                 self.spinner,
                                 alignment=Qt.AlignTop)
        self.spinner.show()

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
        super().__init__(None)
        self.root = root
        self.menu_labels = menu_labels

        self.setWindowTitle(self.TITLE)

        self.layout = layout = QVBoxLayout()
        self.menu = menu = QHBoxLayout()
        self.posts = posts = QScrollArea()
        posts.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
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
            stream = CoubStreamUI()
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
        #       main.py::CoubApp should provide PER_PAGES -> CoubAPI and to this
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
        self.stream.spin()
        self.root.load_menu(index, self._packets[index])
