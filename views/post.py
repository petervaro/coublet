## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.172 (20140814)                       ##
##                                                                            ##
##                            File: views/post.py                             ##
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
from PyQt5.QtWidgets import (QLabel,
                             QWidget,
                             QHBoxLayout,
                             QVBoxLayout,
                             QApplication,
                             QGraphicsDropShadowEffect)

# Import coublet modules
from views.vars import *
from widgets.anim import CoubletAnimatedGifWidget
from widgets.media import CoubletMediaPlayerWidget
from widgets.handler import CoubletMouseEventHandler


#------------------------------------------------------------------------------#
class CoubletPostView(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set flags
        self._post = True
        self._mute = False
        self._stop = True
        self._audio_loop = False

        # Overload painter event (and use underscored names;)
        self.paintEvent = self.on_draw

        # Build the GUI
        self._build_gui1()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load(self, packet=None):
        # Get and set dimension of content (coub)
        width = MEDIA_WIDTH
        height = int(width*packet['ratio'])

        # Store static values
        self._link = packet['perma']

        # Create a video player
        self._player = CoubletMediaPlayerWidget(width=width,
                                                height=height,
                                                thumb_file=packet['thumb'][1],
                                                video_file=packet['video'][1],
                                                audio_file=packet['audio'],
                                                loop_audio=True,
                                                loop_video=True,
                                                error_font=CONSTANTS['text_font_generic'],
                                                error_color=CONSTANTS['text_color_light_selected'],
                                                error_background=CONSTANTS['panel_color_error'])
        # If an error occured during the download
        try:
            self._player.set_error(packet['error'])
        except KeyError:
            pass

        # Build GUI (style)
        self._build_gui2(packet, width, height)

        # Overload event (just for the sake of under-scored names:)
        self.mouseReleaseEvent = self.on_mouse_release

        # Set mouse events
        interval = QApplication.instance().doubleClickInterval()
        self._clicker = CoubletMouseEventHandler(interval,
                                                 l_single=self.play,
                                                 l_double=self.open,
                                                 r_single=self.mute,
                                                 r_double=self.stop)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_draw(self, event):
        # Setup drawing object
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(CONSTANTS['panel_color_light'], Qt.SolidPattern))
        # Draw rounded rectangle
        painter.drawRoundedRect(self.rect(), *(POST_ROUNDNESS,)*2)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_mouse_release(self, event):
        # Handle mouse event
        self._clicker.click(event.button())


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def display_error(self, message):
        # Displaye custom error message on the video
        self._player.set_error(message)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def kill_if_not_visible(self):
        # If post has no visible area
        if self.visibleRegion().isEmpty():
            # Reset that post
            self.kill()


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
        # Reset/stop player
        self._stop = True
        self._player.stop()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def open(self):
        # Stop playing
        self._player.pause()
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
            self._player.set_volume(100)
        # If needs to be muted
        else:
            self._mute = True
            self._player.set_volume(0)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def play(self):
        # If post is not valid
        if not self._post:
            return
        # If playing
        elif self._player.state() == QMediaPlayer.PlayingState:
            # Stop playing the loop
            self._player.pause()
        # If paused
        else:
            # Start playing the loop
            self._stop = False
            self._player.play()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _build_gui1(self):
        # Create layout object for full post and zero-out
        self._layout = layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(*(SMALL_PADDING,)*4)

        # Indicate loading
        loading = CoubletAnimatedGifWidget(CONSTANTS['anim_busy_light'], 32, 16)
        loading.random_frame()
        layout.addWidget(loading, alignment=Qt.AlignHCenter)

        # Set layout for this widget
        self.setLayout(layout)

        # Set size and load content
        self.setFixedSize(MEDIA_WIDTH + 2*SMALL_PADDING, USER_SIZE)

        # FIXME: DropShadow has a "funny" effect on the post,
        #        because of that the full info-bar scrolls away
        #        after the video started playing

        # # Add drop shadow to this widget
        # shadow = QGraphicsDropShadowEffect(self)
        # shadow.setColor(CONSTANTS['shadow_color'])
        # shadow.setBlurRadius(POST_SHADOW_BLUR)
        # shadow.setOffset(0, POST_SHADOW_OFFSET)
        # self.setGraphicsEffect(shadow)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _build_gui2(self, packet, width, height):
        # Remove loadiung indicator
        main_layout = self._layout
        main_layout.itemAt(0).widget().setParent(None)
        main_layout.takeAt(0)

        # Add video and thumb to content
        main_layout.addWidget(self._player)

        # Leading and trailing padding (margins)
        height += SMALL_PADDING*2

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
            avatar_image = CONSTANTS['icon_no_avatar']
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
        title.setFont(CONSTANTS['text_font_title'])
        title.setPalette(CONSTANTS['text_color_dark'])
        text_layout.addWidget(title)

        # Create and add author
        author = QLabel('— {}'.format(packet['name']))
        author.setFont(CONSTANTS['text_font_author'])
        author.setPalette(CONSTANTS['text_color_dark'])
        text_layout.addWidget(author)

        # Add texts to the info bar
        info_layout.addSpacing(SMALL_PADDING)
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
        likes_icon.setPixmap(CONSTANTS['icon_like'])

        likes_text = QLabel(packet['likes'])
        likes_text.setFont(CONSTANTS['text_font_numbers'])
        likes_text.setPalette(CONSTANTS['text_color_dark'])

        likes_layout.addSpacing(SMALL_PADDING)
        likes_layout.addWidget(likes_icon)
        likes_layout.addSpacing(SMALL_PADDING)
        likes_layout.addWidget(likes_text, alignment=Qt.AlignHCenter)

        # Create layout for share-counter and zero-out
        share_layout = QHBoxLayout()
        share_layout.setSpacing(0)
        share_layout.setContentsMargins(*(0,)*4)

        # Create and add shares
        share_icon = QLabel()
        share_icon.setPixmap(CONSTANTS['icon_recoub'])

        share_text = QLabel(packet['share'])
        share_text.setFont(CONSTANTS['text_font_numbers'])
        share_text.setPalette(CONSTANTS['text_color_dark'])

        share_layout.addSpacing(SMALL_PADDING)
        share_layout.addWidget(share_icon)
        share_layout.addSpacing(SMALL_PADDING)
        share_layout.addWidget(share_text, alignment=Qt.AlignHCenter)

        # Add likes and share to social
        social_layout.addLayout(likes_layout)
        social_layout.addLayout(share_layout)

        # Create separator
        separator = QLabel()
        separator.setPixmap(CONSTANTS['other_separator'])

        # Add separator and social to the info bar
        info_layout.addStretch(0)
        info_layout.addWidget(separator)
        info_layout.addSpacing(SMALL_PADDING)
        info_layout.addLayout(social_layout)

        # Add info, increase total height
        main_layout.addSpacing(SMALL_PADDING)
        main_layout.addLayout(info_layout)
        height += avatar_image.height()

        # Add bottom padding
        height += SMALL_PADDING

        # Set size and load content
        self.setFixedHeight(height)
