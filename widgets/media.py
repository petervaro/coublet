## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.060 (20140813)                       ##
##                                                                            ##
##                           File: widgets/media.py                           ##
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
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

#------------------------------------------------------------------------------#
class CoubletMediaPlayerWidget(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, width, height, thumb_file, video_file, looping,
                 error_font=None, parent=None):
        super().__init__(parent)

        self.setFixedSize(width, height)

        # Store static values
        self._error_font = error_font

        # Create thumbnail preview
        self._thumb = thumb = QLabel(self)
        thumb.setPixmap(QPixmap(thumb_file).scaled(width, height))

        # Create video player and its content
        self._video = video = QVideoWidget(self)
        video.setFixedSize(width, height)

        self._player = player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        player.setVideoOutput(video)
        player.error.connect(lambda: self.set_error(self.get_error()))
        player.setMedia(QMediaContent(QUrl.fromLocalFile(video_file)))

        if looping:
            self._loop = False
            player.stateChanged.connect(self.loop)

        self.stop()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def set_error(self, message):
        self._loop = False
        self._video.hide()
        self._thumb.hide()
        layout = QVBoxLayout()
        error_msg = self._player.errorString()
        error_label = QLabel('ERROR: {!r}.'.format(message))
        if self._error_font:
            error_label.setFont(self._error_font)
        layout.addWidget(error_label, alignment=Qt.AlignHCenter)
        self.setLayout(layout)

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

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def get_error(self):
        message = self._player.errorString()
        return message if message else 'unknown from <VideoWithThumbnail>'
