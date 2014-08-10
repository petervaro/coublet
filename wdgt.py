## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.80.980 (20140810)                       ##
##                                                                            ##
##                               File: wdgt.py                                ##
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
from random import random

# Import PyQt5 modules
from PyQt5.QtGui import QMovie, QPixmap, QPalette
from PyQt5.QtCore import Qt, QTimer, QByteArray, QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout

# Module level constants
ICON_AND_LABEL = 0
LABEL_AND_ICON = 1

VERTICAL   = 0
HORIZONTAL = 1

f = lambda *args, **kwargs: None

#------------------------------------------------------------------------------#
class MouseClick:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, interval=300, l_single=f, l_double=f, r_single=f, r_double=f):
        # Create Timer objects, set them and connect events
        self.l_timer = l_timer = QTimer()
        self.r_timer = r_timer = QTimer()
        for i, side in enumerate((l_timer, r_timer)):
            side.setInterval(interval)
            side.setSingleShot(True)
            side.timeout.connect(lambda s=i: self._on_timeout(s))

        # Click counter
        self._counters = [0, 0]

        # Set callbacks
        self._singles = [l_single, r_single]
        self._doubles = [l_double, r_double]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _on_timeout(self, index):
        if self._counters[index] > 1:
            self._doubles[index]()
        else:
            self._singles[index]()
        # Reset counter
        self._counters[index] = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def click(self, button):
        # Clicked by left mouse button
        if button == Qt.LeftButton:
            self._counters[0] += 1
            if not self.l_timer.isActive():
                self.l_timer.start()

        # Clicked by right mouse button
        if button == Qt.RightButton:
            self._counters[1] += 1
            if not self.r_timer.isActive():
                self.r_timer.start()


#------------------------------------------------------------------------------#
class IconLabel(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # TODO: do something with width and height if provided
    def __init__(self, icon, label, order, orientation, font=None, palette=None,
                 width=0, height=0, spacing=0, parent=None, mouse_event_handler=None,
                 padding_left=0, padding_top=0, padding_right=0, padding_bottom=0):
        super().__init__(parent)

        # Create layout
        layout = QHBoxLayout() if orientation else QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(padding_left, padding_top,
                                  padding_right, padding_bottom)
        # Set icon
        image = QLabel()
        image.setPixmap(icon)

        # Set label
        text = QLabel(label)
        if font:
            text.setFont(font)
        if palette:
            text.setPalette(palette)

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


#------------------------------------------------------------------------------#
class VideoWithThumbnail(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, width, height, thumb_file, video_file, looping, parent=None):
        super().__init__(parent)

        self.setFixedSize(width, height)

        # Create thumbnail preview
        self._thumb = thumb = QLabel(self)
        thumb.setPixmap(QPixmap(thumb_file).scaled(width, height))

        # Create video player and its content
        self._video = video = QVideoWidget(self)
        video.setFixedSize(width, height)

        self._player = player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        player.setVideoOutput(video)
        # TODO: add error handling to player
        # player.error.connect(self.on_error)
        player.setMedia(QMediaContent(QUrl.fromLocalFile(video_file)))

        if looping:
            self._loop = False
            player.stateChanged.connect(self.loop)

        self.stop()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def loop(self, *args, **kwargs):
        # If playing => has to be looped => start over!
        if self._loop:
            self._player.play()
        # If paused
        else:
            # Reset looping
            self._loop = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def play(self):
        if self._stopped:
            self._stopped = False
            self._video.show()
            self._thumb.hide()
        self._loop = True
        self._player.play()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def pause(self):
        self._loop = False
        self._player.pause()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def stop(self):
        self._loop = False
        self._stopped = True
        self._thumb.show()
        self._video.hide()
        self._player.stop()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def state(self):
        return self._player.state()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def set_volume(self, volume):
        self._player.setVolume(volume)


#------------------------------------------------------------------------------#
class AnimatedGif(QWidget):

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
        movie.setSpeed(100)
        movie.start()

        label.setMovie(movie)
        layout.addWidget(label)

        self.setLayout(layout)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def random_frame(self):
        # Jump to a random frame
        self._movie.jumpToFrame(int(random() * self._movie.frameCount()))
