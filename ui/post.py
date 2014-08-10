## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.80.984 (20140810)                       ##
##                                                                            ##
##                              File: ui/post.py                              ##
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
import webbrowser

# Import PyQt5 modules
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QPainter, QBrush
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout,
                             QVBoxLayout, QGraphicsDropShadowEffect)

# Import coublet modules
import gui
import wdgt


#------------------------------------------------------------------------------#
class CoubPostUI(QWidget):

    WIDTH = 320

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set flags
        self._post = True
        self._mute = False
        self._stop = True
        self._audio_loop = False

        self.paintEvent = self.on_draw

        self._build_gui1()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load(self, packet=None):
        # Get and set dimension of content (coub)
        width = self.WIDTH
        height = int(width*packet['ratio'])

        # Store static values
        self._link = packet['perma']

        # Create a video player
        self._video = wdgt.VideoWithThumbnail(width=width,
                                              height=height,
                                              thumb_file=packet['thumb'][1],
                                              video_file=packet['video'][1],
                                              looping=True)

        # Create audio player and its content
        audio = packet['audio']
        if audio:
            self.audio_player = audio_player = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
            audio_player.stateChanged.connect(self.on_audio_state_changed)
            audio_player.error.connect(self.on_error)
            # Store MediaContent, otherwise it
            # will be GC'd after stop() or kill()
            self._audio = QMediaContent(QUrl(audio))
            audio_player.setMedia(self._audio)

        # Set error label
        # TODO: place error label to the right position
        #       for testing see on_error's note
        self.error = error = QLabel()
        error.setFont(gui.CONSTANTS['text_font_generic'])

        # Build GUI (style)
        self._build_gui2(packet, width, height)

        # Overload event (just for the sake of under-scored names:)
        self.mouseReleaseEvent = self.on_mouse_release

        # Set mouse events
        interval = QApplication.instance().doubleClickInterval()
        self._clicker = wdgt.MouseClick(interval,
                                        l_single=self.play,
                                        l_double=self.open,
                                        r_single=self.mute,
                                        r_double=self.stop)
        # Hide unneeded widgets
        error.hide()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_draw(self, event):
        # Setup drawing object
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gui.CONSTANTS['panel_color_light'], Qt.SolidPattern))
        # Draw rounded rectangle
        painter.drawRoundedRect(self.rect(), *(gui.POST_ROUNDNESS,)*2)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_mouse_release(self, event):
        # Handle mouse event
        self._clicker.click(event.button())


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_audio_state_changed(self, event):
        # If playing => has to be looped => start over!
        if self._audio_loop:
            self.audio_player.play()
        # If paused
        else:
            # Reset looping
            self._audio_loop = True


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_error(self):
        # TODO: make error label appear on the video itself
        #       test: CoubPost(parent, None) --> error loading media
        self._post = False
        self.error.show()
        self.error.setText('ERROR: ' + self.video_player.errorString().upper())


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def kill(self):
        # If post fully loaded
        try:
            # A wrapper around stop() to be called by the stream
            # when post is not visible and not playing video
            if not self._stop:
                self.stop()
        # If post is loading right now
        except AttributeError:
            pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def stop(self):
        self._video.stop()
        try:
            self._audio_loop = False
            self.audio_player.stop()
        except AttributeError:
            pass
        self._stop = True


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def open(self):
        # Stop playing
        self._audio_loop = False
        self._video.pause()
        try:
            self.audio_player.pause()
        except AttributeError:
            pass
        # Open in browser
        webbrowser.open_new_tab(self._link)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def mute(self):
        # If post is not valid
        if not self._post:
            return
        # If already muted
        elif self._mute:
            self._mute = False
            self._video.set_volume(100)
            try:
                self.audio_player.setVolume(100)
            except AttributeError:
                pass
        # If needs to be muted
        else:
            self._mute = True
            self._video.set_volume(0)
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
        elif self._video.state() == QMediaPlayer.PlayingState:
            # Stop playing the loop
            self._audio_loop = False
            self._video.pause()
            try:
                self.audio_player.pause()
            except AttributeError:
                pass
        # If paused
        else:
            # Start playing the loop
            self._stop = False
            self._audio_loop = True
            self._video.play()
            try:
                self.audio_player.play()
            except AttributeError:
                pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _build_gui1(self):
        # Create layout object for full post and zero-out
        self._layout = layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(*(gui.SMALL_PADDING,)*4)

        # Indicate loading
        loading = wdgt.AnimatedGif(gui.CONSTANTS['anim_busy'], 32, 16)
        loading.random_frame()
        layout.addWidget(loading, alignment=Qt.AlignHCenter)

        # Set layout for this widget
        self.setLayout(layout)

        # Set size and load content
        self.setFixedSize(self.WIDTH + 2*gui.SMALL_PADDING, gui.USER_SIZE)

        # FIXME: DropShadow has a "funny" effect on the post,
        #        because of that the full info-bar scrolls away
        #        after the video started playing

        # # Add drop shadow to this widget
        # shadow = QGraphicsDropShadowEffect(self)
        # shadow.setColor(gui.CONSTANTS['shadow_color'])
        # shadow.setBlurRadius(gui.POST_SHADOW_BLUR)
        # shadow.setOffset(0, gui.POST_SHADOW_OFFSET)
        # self.setGraphicsEffect(shadow)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _build_gui2(self, packet, width, height):
        # Remove loadiung indicator
        main_layout = self._layout
        main_layout.takeAt(0)

        # Add video and thumb to content
        main_layout.addWidget(self._video)

        # Leading and trailing padding (margins)
        height += gui.SMALL_PADDING*2

        # Create layout object for info bar and zero-out
        info_layout = QHBoxLayout()
        info_layout.setSpacing(0)
        info_layout.setContentsMargins(*(0,)*4)

        # Create and add avatar if any,
        # else use the default placeholder
        avatar = QLabel()
        avatar_image_path = packet['user'][1]
        if avatar_image_path:
            avatar_image = QPixmap(avatar_image_path)
        else:
            avatar_image = gui.CONSTANTS['icon_no_avatar']
        avatar.setPixmap(avatar_image)
        info_layout.addWidget(avatar)

        # Create layout for text and zero-out
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        text_layout.setContentsMargins(*(0,)*4)

        # Create and add title
        title = QLabel('“{}”'.format(packet['title']))
        # TODO: wrapping properly!
        # title.setWordWrap(True)
        title.setFont(gui.CONSTANTS['text_font_title'])
        title.setPalette(gui.CONSTANTS['text_color_dark'])
        text_layout.addWidget(title)

        # Create and add author
        author = QLabel('— {}'.format(packet['name']))
        author.setFont(gui.CONSTANTS['text_font_author'])
        author.setPalette(gui.CONSTANTS['text_color_dark'])
        text_layout.addWidget(author)

        # Add texts to the info bar
        info_layout.addSpacing(gui.SMALL_PADDING)
        info_layout.addLayout(text_layout)

        # Create layout for social and zero-out
        social_layout = QVBoxLayout()
        social_layout.setSpacing(0)
        social_layout.setContentsMargins(*(0,)*4)

        # Create layout for like-counter and zero-out
        likes_layout = QHBoxLayout()
        likes_layout.setSpacing(0)
        likes_layout.setContentsMargins(*(0,)*4)

        # Create and add likes
        likes_icon = QLabel()
        likes_icon.setPixmap(gui.CONSTANTS['icon_like'])

        likes_text = QLabel(packet['likes'])
        likes_text.setFont(gui.CONSTANTS['text_font_numbers'])
        likes_text.setPalette(gui.CONSTANTS['text_color_dark'])

        likes_layout.addSpacing(gui.SMALL_PADDING)
        likes_layout.addWidget(likes_icon)
        likes_layout.addSpacing(gui.SMALL_PADDING)
        likes_layout.addWidget(likes_text, alignment=Qt.AlignHCenter)

        # Create layout for share-counter and zero-out
        share_layout = QHBoxLayout()
        share_layout.setSpacing(0)
        share_layout.setContentsMargins(*(0,)*4)

        # Create and add shares
        share_icon = QLabel()
        share_icon.setPixmap(gui.CONSTANTS['icon_recoub'])

        share_text = QLabel(packet['share'])
        share_text.setFont(gui.CONSTANTS['text_font_numbers'])
        share_text.setPalette(gui.CONSTANTS['text_color_dark'])

        share_layout.addSpacing(gui.SMALL_PADDING)
        share_layout.addWidget(share_icon)
        share_layout.addSpacing(gui.SMALL_PADDING)
        share_layout.addWidget(share_text, alignment=Qt.AlignHCenter)

        # Add likes and share to social
        social_layout.addLayout(likes_layout)
        social_layout.addLayout(share_layout)

        # Create separator
        separator = QLabel()
        separator.setPixmap(gui.CONSTANTS['other_separator'])

        # Add separator and social to the info bar
        info_layout.addStretch(0)
        info_layout.addWidget(separator)
        info_layout.addSpacing(gui.SMALL_PADDING)
        info_layout.addLayout(social_layout)

        # Add info, increase total height
        main_layout.addSpacing(gui.SMALL_PADDING)
        main_layout.addLayout(info_layout)
        height += avatar_image.height()

        # Add bottom padding
        height += gui.SMALL_PADDING

        # Set size and load content
        self.setFixedHeight(height)
