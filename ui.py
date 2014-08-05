## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.61.568 (20140805)                       ##
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
                             QVBoxLayout, QWidget, QDesktopWidget, QScrollArea,
                             QGraphicsDropShadowEffect)

# Import coub modules
import gui
import wdgt
from static import RESOURCES

# TODO: REFRESH DATA
#       SOLVE THE NEWEST, RANDOM NOT LOADING PROBLEM
#         ^
#       ADD USER STREAM
#       ON REFRESH, SCROLL TO LAST POST
#       SOLVE DOWNLOAD/PLACING ORDER PROBLEM
#       PRETTIFY GUI
#       REFACTOR CODE AND REPO
#
#       Harry Potter < 3:02:00

#------------------------------------------------------------------------------#
# TODO: legacy remove this!
PADDING = gui.SMALL_PADDING

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
        gui.build_post_style(self, packet, video, thumb, width, height)

        # Overload event (just for the sake of under-scored names:)
        self.mouseReleaseEvent = self.on_mouse_release

        # Set mouse events
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



#------------------------------------------------------------------------------#
class CoubStreamUI(QWidget):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, index, parent=None):
        super().__init__(parent)

        # Store static values
        self.index = index
        # Build UI
        gui.build_stream_style(self)
        # Initially hide spinner
        self.spinner.hide()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def add_post(self, packet):
        layout = self.layout
        self.spinner.hide()
        # Insert before space
        post_index = layout.count() - 2
        layout.insertWidget(post_index, CoubPostUI(packet), alignment=Qt.AlignTop)
        layout.insertSpacing(post_index, gui.POST_SPACING)

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

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, root, x, y, width, height, title, menu_labels, packet_count):
        super().__init__(None)

        # Set CONSTANTS
        gui.set_gui_constants(self)

        # Store static values
        self.root = root
        self.menu_labels = menu_labels
        # Maximum packet count before load data
        # a stream can load more packets
        self.packet_count = packet_count
        self.title = title


        self.setWindowTitle(title)

        gui.build_app_style(self)


        self.layout = layout = QVBoxLayout()
        self.menu = menu = QHBoxLayout()
        self.posts = posts = QScrollArea()
        posts.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        posts.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        posts.verticalScrollBar().valueChanged.connect(self._on_update_stream)
        posts.setFrameShape(QFrame.NoFrame)

        menu.setSpacing(0)
        menu.setContentsMargins(0, 0, 0, 0)

        menu_bar = QWidget()

        menu_pad = QVBoxLayout()
        menu_pad.setSpacing(0)
        menu_pad.setContentsMargins(0, 0, 0, 0)

        menu_pad.addSpacing(2*PADDING)
        menu_pad.addLayout(menu)
        menu_pad.addSpacing(2*PADDING)

        menu_color = QPalette()
        menu_color.setColor(QPalette.Background, QColor(*(0x18,)*3))
        menu_bar.setPalette(menu_color)
        menu_bar.setAutoFillBackground(True)


        menu_bar.setLayout(menu_pad)

        # Finalise layout
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(posts)
        layout.addWidget(menu_bar)
        self.setLayout(layout)

        self.streams = streams = []
        self._packets = packets = []
        self._packet_counter = packet_counter = []

        menu.addSpacing(2*PADDING)
        for i, menu_item in enumerate(self.menu_labels):
            # If not the first item, add
            # auto-stretching before it
            if i:
                menu.addStretch(0)

            # Add menu item
            click = wdgt.MouseClick(l_single=lambda n=i: self.on_menu_button_pressed(n))
            menu_button = wdgt.IconLabel(icon=gui.CONSTANTS['icon_' + menu_item],
                                         label=menu_item.upper(),
                                         order=wdgt.ICON_AND_LABEL,
                                         orientation=wdgt.HORIZONTAL,
                                         font=gui.CONSTANTS['text_font_generic'],
                                         palette=gui.CONSTANTS['text_color_light'],
                                         spacing=PADDING,
                                         mouse_event_handler=click)
            menu.addWidget(menu_button)

            # Add stream
            stream = CoubStreamUI(i)
            streams.append(stream)
            # Add stream specific packet queue
            packets.append(queue.Queue())
            packet_counter.append(0)

        menu.addSpacing(2*PADDING)

        # Set last stream selected
        self.stream = stream

        # Just for the sake of under-scored names ;)
        self.closeEvent = self.on_exit
        # TODO: implerment real up and "over scroll" by
        #       overwriting wheelEvent
        #       self.wheelEvent = self.on_mouse_scroll
        #       and with event.pixelDelta() -> check QWheelEvent

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
                self.stream.add_post(self._packets[index].get_nowait())
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
        self.setWindowTitle('{} | {}'.format(self.title,
                                             self.menu_labels[index].upper()))
        # And set new stream
        posts.setWidget(self.stream)
        posts.setWidgetResizable(True)
        if not self.stream.layout.count():
            self.load_more(index)
