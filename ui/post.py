## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.70.672 (20140806)                       ##
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
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout,
                             QVBoxLayout, QGraphicsDropShadowEffect)

# Import coublet modules
import gui
import wdgt


#------------------------------------------------------------------------------#
class CoubPostUI(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, packet=None, parent=None):
        super().__init__(parent)

        # Get and set dimension of content (coub)
        width = 320
        height = int(width*packet['ratio'])

        # Set flags
        self._post = True
        self._mute = False
        self._audio_loop = False
        self._video_loop = False

        # Store static values
        self._link = packet['perma']

        # Create thumbnail preview
        self.thumb = thumb = QLabel(self)
        thumb.setPixmap(QPixmap(packet['thumb'][1]).scaled(width, height))

        # Create video player and its content
        self.video = video = QVideoWidget(self)
        video.setFixedSize(width, height)

        self.video_player = video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        video_player.setVideoOutput(video)
        video_player.stateChanged.connect(self.on_video_state_changed)
        video_player.error.connect(self.on_error)
        video_player.setMedia(QMediaContent(QUrl.fromLocalFile(packet['video'][1])))

        # Create audio player and its content
        audio = packet['audio']
        if audio:
            self.audio_player = audio_player = QMediaPlayer(None)
            audio_player.stateChanged.connect(self.on_audio_state_changed)
            audio_player.error.connect(self.on_error)
            audio_player.setMedia(QMediaContent(QUrl(audio)))

        # Set error label
        # TODO: place error label to the right position
        #       for testing see on_error's note
        self.error = error = QLabel()
        error.setFont(gui.CONSTANTS['text_font_generic'])

        # Build GUI (style)
        self.build_gui(packet, width, height)

        # Overload event (just for the sake of under-scored names:)
        self.mouseReleaseEvent = self.on_mouse_release

        # Set mouse events
        # TODO: double right click => restart video and audio
        interval = QApplication.instance().doubleClickInterval()
        self._clicker = wdgt.MouseClick(interval,
                                        l_single=self.play,
                                        l_double=self.open,
                                        r_single=self.mute)
        # Hide unneeded widgets
        video.hide()
        error.hide()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_mouse_release(self, event):
        # Handle mouse event
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
        self.error.show()
        self.error.setText('ERROR: ' + self.video_player.errorString().upper())

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
            # TODO: delete widget and its content
            self.thumb.hide()
            self.video.show()
            self.video_player.play()
            try:
                self.audio_player.play()
            except AttributeError:
                pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def build_gui(self, packet, width, height):
        # Create layout object for full post and zero-out
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(*(0,)*4)

        # Create layout for content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(*(0,)*4)

        # Add video and thumb to content
        content_layout.addSpacing(gui.SMALL_PADDING)
        content_layout.addWidget(self.video)
        content_layout.addWidget(self.thumb)
        content_layout.addSpacing(gui.SMALL_PADDING)

        # Add layout to main layout
        main_layout.addSpacing(gui.SMALL_PADDING)
        height += gui.SMALL_PADDING
        main_layout.addLayout(content_layout)

        # Add padding, increase total height
        main_layout.addSpacing(gui.SMALL_PADDING)
        height += gui.SMALL_PADDING

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
        info_layout.addSpacing(gui.SMALL_PADDING)
        info_layout.addWidget(avatar)


        # Create layout for text and zero-out
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        text_layout.setContentsMargins(*(0,)*4)

        # Create and add title
        # TODO: wrap words of title and author
        title = QLabel('“{}”'.format(packet['title']))
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
        info_layout.addSpacing(gui.SMALL_PADDING)

        # Add info, increase total height
        main_layout.addLayout(info_layout)
        height += avatar_image.height()

        # Add bottom padding
        main_layout.addSpacing(gui.SMALL_PADDING)
        height += gui.SMALL_PADDING

        # Set layout for this widget
        self.setLayout(main_layout)

        # Set color of this widget
        self.setAutoFillBackground(True)
        self.setPalette(gui.CONSTANTS['panel_color_light'])


        # Set size and load content
        self.setFixedSize(width + 2*gui.SMALL_PADDING, height)

        # Make it rounded
        gui._rounded_rectangle(self, *(gui.SMALL_PADDING,)*4)

        # FIXME: DropShadow has a "funny" effect on the post,
        #        because of that the full info-bar scrolls away
        #        after the video started playing

        # # Add drop shadow to this widget
        # shadow = QGraphicsDropShadowEffect(widget)
        # shadow.setColor(gui.CONSTANTS['shadow_color'])
        # shadow.setBlurRadius(15)
        # shadow.setOffset(0, 3)
        # self.setGraphicsEffect(shadow)
