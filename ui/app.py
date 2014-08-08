## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.70.799 (20140808)                       ##
##                                                                            ##
##                              File: ui/app.py                               ##
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
import queue

# Import PyQt5 modules
from PyQt5.QtCore import Qt, QTimer, QElapsedTimer
from PyQt5.QtWidgets import (QWidget, QFrame, QScrollArea, QDesktopWidget,
                             QHBoxLayout, QVBoxLayout)

# Import coublet modules
import gui
import wdgt
from .stream import CoubStreamUI

# TODO: REFRESH DATA
#       ON REFRESH, SCROLL TO LAST POST
#       PRETTIFY GUI
#       REFACTOR CODE AND REPO
#
#       Harry Potter @ 0:33:50

#------------------------------------------------------------------------------#
class CoubAppUI(QWidget):

    SCROLL_POSITIVE = 30
    SCROLL_NEGATIVE = -SCROLL_POSITIVE

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, root, dimension, title, menu_labels, max_packets):
        super().__init__(None)

        # Set CONSTANTS
        gui.set_gui_constants(self)

        # Store static values
        self._root = root
        self._menu_labels = menu_labels
        self._max_packets = max_packets

        # Set window title
        self._title = title
        self.setWindowTitle(title)

        self._bounce = 0

        # Storages
        self._streams = []
        self._packets = []
        self._loading = []

        # Build GUI
        self._build_gui()

        # Overload closing and scrolling event, and rename it just
        # for the sake of under-scored names ;)
        self.closeEvent = self.on_exit
        self.wheelEvent = self.on_mouse_scroll

        # Unpack dimension data
        x, y, width, height = dimension

        # If position have not been set before
        if x is NotImplemented:
            screen = QDesktopWidget().screenGeometry()
            x, y = (screen.width() - width) / 2, (screen.height() - height) / 2
        # Set window position and dimension
        self.setGeometry(x, y, width, height)
        self.setMaximumWidth(width)

        self._xxx = True

        # Load first stream
        self.on_menu_button_pressed(0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_mouse_scroll(self, event):
        # TODO: on stream start (first visit) jumpt at the end of
        #       scroll_up arrow, probably using one these?
        #       self._posts.verticalScrollBar().value()      # getter
        #       self._posts.verticalScrollBar().setValue()   # setter

        # Get index of currently active stream
        # TODO: consider: we don't need active stream, we need active index!
        index = self._active_stream.index
        # If there is no on-going downloading
        if not self._loading[index]:
            # Get the "stregth" of scroll
            dy = event.pixelDelta().y()
            # If "hard" enoough downward
            if dy < self.SCROLL_NEGATIVE:
                self._load_more_posts(index)
                print('[SCROLL] loading more...')
            # If "hard" enough upward
            elif dy > self.SCROLL_POSITIVE:
                self._reload_posts(index)
                print('[SCROLL] refreshing...')

        # Kill posts in stream which are not visible
        self._active_stream.reset_unseen_posts()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_exit(self, event):
        # FIXME: probably we are storing the wrong dimensions,
        #        window is going upper and upper om each run
        #        or is it wrongly loaded ???
        dim = self.frameGeometry()
        self._root.on_exit((dim.x(), dim.y(), dim.width(), dim.height()))
        event.accept()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_load_posts(self, index):
        try:
            # Load as many posts as possible
            while True:
                self._streams[index].load_post(self._packets[index].get_nowait())
                self._loading[index] -= 1
                # If fetched all data, stop scheduling
                if not self._loading[index]:
                    self._streams[index].spin_off()
                    return
        except queue.Empty:
            # Start loading posts again later
            QTimer.singleShot(500, lambda i=index: self.on_load_posts(index))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_menu_button_pressed(self, index):
        # Get preferred stream
        active_stream = self._streams[index]

        # Preferred stream is not yet active
        if active_stream is not self._active_stream:
            # Set stream active
            self._active_stream = active_stream

            # Remove previously active stream
            posts = self._posts
            posts.takeWidget()

            # Indicate change in window title
            self.setWindowTitle('{} | {}'.format(self._title,
                                                 self._menu_labels[index].upper()))
            # And set new stream
            posts.setWidget(self._active_stream)
            posts.setWidgetResizable(True)

            # If first visit of active stream
            if not self._active_stream.visited:
                self._active_stream.visited = True
                self._load_more_posts(index)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _load_more_posts(self, index):
        # Start loading posts
        self._root.start_loading_posts(index, self._packets[index])
        # Set loading counter
        self._loading[index] = self._max_packets
        # Create slots
        self._active_stream.add_posts(self._max_packets)
        # Start checking if processed data arrived to queue
        self.on_load_posts(index)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _reload_posts(self, index):
        # Refresh posts
        pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _build_gui(self):
        # Storages
        streams = self._streams
        packets = self._packets
        loading = self._loading

        # Create layout for the entire application and zero-out
        self.layout = main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create and add scrollable area for streams
        self._posts = posts = QScrollArea()
        posts.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        posts.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # posts.verticalScrollBar().valueChanged.connect(self._on_update_stream)
        posts.setFrameShape(QFrame.NoFrame)
        main_layout.addWidget(posts)

        # Create menu-bar
        menu_bar = QWidget()
        menu_bar.setPalette(gui.CONSTANTS['panel_color_darker'])
        menu_bar.setAutoFillBackground(True)

        # Create layout for menu-bar and zero-out
        menu_bar_layout = QVBoxLayout()
        menu_bar_layout.setSpacing(0)
        menu_bar_layout.setContentsMargins(0, 0, 0, 0)

        # Create layout for menu buttons and zero-out
        menu_buttons_layout = QHBoxLayout()
        menu_buttons_layout.setSpacing(0)
        menu_buttons_layout.setContentsMargins(0, 0, 0, 0)

        # Add menu-buttons to menu-bar
        menu_bar_layout.addSpacing(2*gui.SMALL_PADDING)
        menu_bar_layout.addLayout(menu_buttons_layout)
        menu_bar_layout.addSpacing(2*gui.SMALL_PADDING)

        # Assign layout and add menu-bar to app
        menu_bar.setLayout(menu_bar_layout)
        main_layout.addWidget(menu_bar)

        # Add buttons and spacess to menu-buttons layout
        menu_buttons_layout.addSpacing(2*gui.SMALL_PADDING)
        for i, menu_item in enumerate(self._menu_labels):
            # If not the first item, add
            # auto-stretching before it
            if i:
                menu_buttons_layout.addStretch(0)

            # Add menu item
            click = wdgt.MouseClick(l_single=lambda n=i: self.on_menu_button_pressed(n))
            menu_button = wdgt.IconLabel(icon=gui.CONSTANTS['icon_' + menu_item],
                                         label=menu_item.upper(),
                                         order=wdgt.ICON_AND_LABEL,
                                         orientation=wdgt.HORIZONTAL,
                                         font=gui.CONSTANTS['text_font_generic'],
                                         palette=gui.CONSTANTS['text_color_light'],
                                         spacing=gui.SMALL_PADDING,
                                         mouse_event_handler=click)
            menu_buttons_layout.addWidget(menu_button)
            # Add stream
            stream = CoubStreamUI(i)
            streams.append(stream)
            # Add stream specific packet queue
            packets.append(queue.Queue())
            loading.append(0)
        # Tail padding
        menu_buttons_layout.addSpacing(2*gui.SMALL_PADDING)

        self.setLayout(main_layout)
        self.setPalette(gui.CONSTANTS['panel_color_dark'])
        # Set last stream as selected
        self._active_stream = stream
