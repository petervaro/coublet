## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.172 (20140814)                       ##
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
    def __init__(self, width, height, thumb_file, video_file, audio_file=None,
                 loop_video=False, loop_audio=False, error_font=None,
                 error_color=None, error_background=None, parent=None):
        super().__init__(parent)

        # Restrict size
        self.setFixedSize(width, height)

        # Store static values
        self._error_font  = error_font
        self._error_color = error_color
        self._error_background = error_background

        # Create thumbnail preview
        self._thumb = thumb = QLabel(self)
        thumb.setPixmap(QPixmap(thumb_file).scaled(width, height))

        # Create video player and its content
        self._video = video = QVideoWidget(self)
        video.setFixedSize(width, height)

        # Set video player file
        self._video_player = video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        video_player.setVideoOutput(video)
        video_player.error.connect(lambda: self.set_error(self.get_error()))
        video_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_file)))

        # Set looping for video
        if loop_video:
            self._loop_video = False
            video_player.stateChanged.connect(self.on_video_player_state_changed)

        # Set separate playe for audio file if any
        if audio_file:
            self._audio_player = audio_player = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
            audio_player.error.connect(lambda: self.set_error(self.get_error()))
            # Store MediaContent, otherwise it will be GC'd after stop()
            self._audio = QMediaContent(QUrl(audio_file))
            audio_player.setMedia(self._audio)
            # Ste looping for audio
            if loop_audio:
                self._loop_audio = False
                audio_player.stateChanged.connect(self.on_audio_player_state_changed)

        # Make sure all flags are set and
        # only the proper widgets are visible
        self.stop()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_video_player_state_changed(self, event):
        # If playing => has to be looped => start over!
        if self._loop_video:
            self._video_player.play()
        # If paused
        else:
            # Reset looping
            self._loop_video = True


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_audio_player_state_changed(self, event):
        # If playing => has to be looped => start over!
        if self._loop_audio:
            self._audio_player.play()
        # If paused
        else:
            # Reset looping
            self._loop_audio = True


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def set_error(self, message):
        try:
            self._loop_audio = False
        except AttributeError:
            pass
        self._loop_video = False
        self._video.hide()
        self._thumb.hide()
        layout = QVBoxLayout()
        error_msg = self._video_player.errorString()
        error_label = QLabel('ERROR: {}'.format(message.upper()))
        if self._error_font:
            error_label.setFont(self._error_font)
        if self._error_color:
            error_label.setPalette(self._error_color)
        if self._error_background:
            self.setPalette(self._error_background)
            self.setAutoFillBackground(True)
        layout.addWidget(error_label, alignment=Qt.AlignHCenter)
        self.setLayout(layout)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def get_error(self):
        message = self._video_player.errorString()
        if message:
            return '{!r} @video'.format(message)
        try:
            message = self._audio_player.errorString()
            if message:
                return '{!r} @audio'.format(message)
        except AttributeError:
            pass
        return 'unknown'


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def play(self):
        if self._stopped:
            self._stopped = False
            self._video.show()
            self._thumb.hide()
        try:
            self._loop_audio = True
            self._audio_player.play()
        except AttributeError:
            pass
        self._loop_video = True
        self._video_player.play()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def pause(self):
        try:
            self._loop_audio = False
            self._audio_player.pause()
        except AttributeError:
            pass
        self._loop_video = False
        self._video_player.pause()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def stop(self):
        self._stopped = True
        self._thumb.show()
        self._video.hide()
        try:
            self._loop_audio = False
            self._audio_player.stop()
        except AttributeError:
            pass
        self._loop_video = False
        self._video_player.stop()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def state(self):
        return self._video_player.state()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def set_volume(self, volume):
        try:
            self._audio_player.setVolume(volume)
        except AttributeError:
            pass
        self._video_player.setVolume(volume)
