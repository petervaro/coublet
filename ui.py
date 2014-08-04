## INFO ########################################################################
##                                                                            ##
##                                  COUB App                                  ##
##                                  ========                                  ##
##                                                                            ##
##      Cross-platform desktop application for following posts from COUB      ##
##                       Version: 0.5.61.455 (20140804)                       ##
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
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor
from PyQt5.QtCore import QDir, Qt, QUrl, QTimer, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QFrame,
                             QVBoxLayout, QWidget, QDesktopWidget, QScrollArea)

# Import coub modules
import wdgt
from static import RESOURCES


# TODO: Create a global variable here called CONSTANTS,
#       fill it with Q* objects during the initialisation of
#       CoubAppUI, and add all constant objects, like the 'recoub'
#       icon or the fonts.

PADDING = 5

#------------------------------------------------------------------------------#
class CoubPostUI(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, fonts, packet=None, parent=None):
        super().__init__(parent)

        # Get proper dimensions
        width = 320
        height = int(width * packet['ratio'])

        # Flags
        self._post = True
        self._mute = False
        self._audio_loop = False
        self._video_loop = False

        # Store perma-link
        self._link = packet['perma']

        # Preview
        thumb = QPixmap(packet['thumb'][1])

        self.image = image = QLabel(self)
        image.setPixmap(thumb.scaled(width, height))

        # Media players
        self.video_player = video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        # Video Area
        self.video = video = QVideoWidget(self)
        video.setFixedSize(width, height)
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
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addSpacing(PADDING)

        sub_layout = QVBoxLayout()
        sub_layout.setSpacing(0)
        sub_layout.setContentsMargins(0, 0, 0, 0)
        sub_layout.addSpacing(PADDING)
        sub_layout.addWidget(video)
        sub_layout.addWidget(image)

        sub_layout.addSpacing(PADDING)
        height += PADDING

        # Icons
        avatar = QLabel()
        avatar.setPixmap(QPixmap(packet['user'][1]))
        likes_icon = QLabel()
        likes_icon.setPixmap(QPixmap(RESOURCES['like']))
        share_icon = QLabel()
        share_icon.setPixmap(QPixmap(RESOURCES['recoub']))

        info = QHBoxLayout()
        info.addWidget(avatar)
        height += 38

        info.addSpacing(PADDING)

        text_color = QPalette()
        text_color.setColor(QPalette.Foreground, QColor(0, 0, 0, 153))  # 60% alpha

        info_text = QVBoxLayout()

        coub_text = QLabel('“{}”'.format(packet['title']))
        coub_text.setFont(fonts['title'])
        coub_text.setPalette(text_color)
        info_text.addWidget(coub_text)

        user_name = QLabel('— {}'.format(packet['name']))
        user_name.setFont(fonts['user_name'])
        user_name.setPalette(text_color)
        info_text.addWidget(user_name)

        info.addLayout(info_text)

        info.addStretch(0)

        social = QVBoxLayout()

        likes = QHBoxLayout()
        likes.addWidget(likes_icon)
        likes.addSpacing(PADDING)
        likes_text = QLabel(packet['likes'])
        likes_text.setFont(fonts['numbers'])
        likes_text.setPalette(text_color)
        likes.addWidget(likes_text, alignment=Qt.AlignRight)
        social.addLayout(likes)

        share = QHBoxLayout()
        share.addWidget(share_icon)
        share.addSpacing(PADDING)
        share_text = QLabel(packet['share'])
        share_text.setFont(fonts['numbers'])
        share_text.setPalette(text_color)
        share.addWidget(share_text, alignment=Qt.AlignRight)
        social.addLayout(share)

        info.addLayout(social)
        sub_layout.addLayout(info)

        sub_layout.addWidget(error_label)
        sub_layout.addSpacing(PADDING)
        height += PADDING

        main_layout.addLayout(sub_layout)
        main_layout.addSpacing(PADDING)
        self.setLayout(main_layout)

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
        self.setFixedSize(width + 2*PADDING, height + 2*PADDING)

        # Set color
        background = QPalette()
        background.setColor(QPalette.Background, QColor(*(0xB8,)*3))
        self.setAutoFillBackground(True)
        self.setPalette(background)

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
    def __init__(self, index, fonts, parent=None):
        super().__init__(parent)

        self.index = index

        # Set layout
        self.layout = layout = QVBoxLayout()

        pad = 10
        self.spinner = wdgt.AnimatedGif(file=RESOURCES['spinner'],
                                        width=20,
                                        height=20,
                                        padding_x=pad,
                                        padding_y=pad)
        self.spinner.hide()

        layout.setSpacing(0)
        layout.setContentsMargins(pad, 0, 0, 0)

        self.scroll_label_u = wdgt.IconLabel(file=RESOURCES['scroll_up'],
                                             label='SCROLL UP TO REFRESH',
                                             font=fonts['ui_generic'],
                                             order=wdgt.LABEL_AND_ICON,
                                             orientation=wdgt.VERTICAL,
                                             width=10,
                                             height=10,
                                             padding_x=pad,
                                             padding_y=pad)
        layout.addWidget(self.scroll_label_u)

        layout.addStretch(0)

        self.scroll_label_d = wdgt.IconLabel(file=RESOURCES['scroll_down'],
                                             label='SCROLL DOWN TO LOAD MORE',
                                             font=fonts['ui_generic'],
                                             order=wdgt.ICON_AND_LABEL,
                                             orientation=wdgt.VERTICAL,
                                             width=10,
                                             height=10,
                                             padding_x=pad,
                                             padding_y=pad)
        layout.addWidget(self.scroll_label_d)


        self.setLayout(layout)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def add_posts(self, fonts, *packets):
        # Add new posts to stream
        layout = self.layout
        self.spinner.hide()
        for packet in packets:
            # Insert before space
            post_index = layout.count() - 2
            layout.insertWidget(post_index,
                                CoubPostUI(fonts, packet),
                                alignment=Qt.AlignTop)
            layout.insertSpacing(post_index, 10)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def spin(self, reload=False):
        # Insert before space
        length = self.layout.count()
        self.layout.insertWidget(1 if length == 1 or reload else length - 2,
                                 self.spinner,
                                 alignment=Qt.AlignHCenter)
        self.spinner.show()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def clear(self):
        # Remove all posts from stream
        for i in reversed(range(self.layout.count())):
            # ??? setParent() or close() ???
            self.layout.itemAt(i).widget().setParent(None)



#------------------------------------------------------------------------------#
class CoubAppUI(QWidget):

    TITLE = 'COUBLET'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, root, x, y, width, height, menu_labels, packet_count):
        super().__init__(None)
        self.root = root
        self.menu_labels = menu_labels

        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(*(0x38,)*3))
        self.setPalette(palette)

        self.packet_count = packet_count

        sans = 'Source Sans Pro'
        self.fonts = {'title'     : QFont(sans, 16, QFont.Bold),
                      'user_name' : QFont(sans, 10, QFont.Normal, italic=True),
                      'numbers'   : QFont(sans, 12, QFont.Normal),
                      'ui_generic': QFont(sans, 10, QFont.Normal)}

        self.setWindowTitle(self.TITLE)

        self.layout = layout = QVBoxLayout()
        self.menu = menu = QHBoxLayout()
        self.posts = posts = QScrollArea()
        posts.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        posts.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        posts.verticalScrollBar().valueChanged.connect(self._on_update_stream)
        posts.setFrameShape(QFrame.NoFrame)

        # Finalise layout
        menu.setSpacing(0)
        menu.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(posts)
        layout.addSpacing(PADDING)
        layout.addLayout(menu)
        layout.addSpacing(PADDING)
        self.setLayout(layout)

        self.streams = streams = []
        self._packets = packets = []
        self._packet_counter = packet_counter = []

        color = QPalette()
        color.setColor(QPalette.Foreground, QColor(0xFF, 0xFF, 0xFF, 0x9C))
        font = self.fonts['ui_generic']

        menu.addSpacing(PADDING)
        for i, menu_item in enumerate(self.menu_labels):
            if i:
                menu.addStretch(0)
            # Add menu item
            p = QPixmap('img/{}.png'.format(menu_item))
            menu_icon = QLabel()
            menu_icon.setPixmap(p)
            # menu_button = wdgt.IconLabel(file='img/{}.png'.format(menu_item),
            #                              label=menu_item.upper(),
            #                              order=wdgt.ICON_AND_LABEL,
            #                              orientation=wdgt.HORIZONTAL,
            #                              font=self.fonts['ui_generic'],
            #                              color=QColor(0xFF, 0xFF, 0xFF, 0x9C),
            #                              padding_x=PADDING,
            #                              padding_y=PADDING)
            menu_text = QLabel(menu_item.upper())
            menu_text.setFont(font)
            menu_text.setPalette(color)
            # b is needed because of the implementation `void triggered(bool = 0)`
            # menu_button.clicked.connect(lambda b, n=i: self.on_menu_button_pressed(n))
            menu.addWidget(menu_icon)
            menu.addSpacing(PADDING)
            menu.addWidget(menu_text)
            # Add stream
            stream = CoubStreamUI(i, self.fonts)
            streams.append(stream)
            # Add stream specific packet queue
            packets.append(queue.Queue())
            packet_counter.append(0)

        menu.addSpacing(PADDING)

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
        self.load_more(0)
        # Start checking if Queue has items
        self.on_load_posts(0)

    # Scrolling related stuffs:
    #
    # self.posts.verticalScrollBar().value()      # getter
    # self.posts.verticalScrollBar().setValue()   # setter

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
                self.stream.add_posts(self.fonts, self._packets[index].get_nowait())
                self._packet_counter[index] -= 1
        except queue.Empty:
            pass
        finally:
            # Start loading posts again later
            QTimer.singleShot(500, lambda i=index: self.on_load_posts(index))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load_more(self, index):
        # Load data
        self.stream.spin()
        self.root.load_menu(index, self._packets[index])
        self._packet_counter[index] = self.packet_count

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def reload(self, index):
        # Refresh posts
        self.stream.spin(reload=True)


        #   TODO: REFRESH DATA
        #         SOLVE THE NEWEST, RANDOM NOT LOADING PROBLEM
        #         ADD USER STREAM
        #         ON REFRESH SCROLL TO LAST POST
        #         SOLVE DOWNLOAD/PLACING ORDER PROBLEM
        #         PRETTIFY GUI
        #         REFACTOR CODE AND REPO
        #
        #         Harry Potter < 7:21:00


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _on_update_stream(self, value):
        index = self.stream.index
        # If there is no on-going downloading
        if not self._packet_counter[index]:
            # If load more posts
            if value == self.posts.verticalScrollBar().maximum():
                self.load_more(index)
                print('[SCROLL] loading more...')
            # If reload posts
            elif not value:
                self.reload(index)
                print('[SCROLL] refreshing...')

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
        if not self.stream.layout.count():
            self.load_more(index)
