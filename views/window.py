## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.069 (20140813)                       ##
##                                                                            ##
##                           File: views/window.py                            ##
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
from PyQt5.QtCore import Qt, QTimer, QElapsedTimer
from PyQt5.QtWidgets import (QWidget, QFrame, QScrollArea, QDesktopWidget,
                             QHBoxLayout, QVBoxLayout)

# Import Coublet modules
from views.vars import *
from models.cache import CACHE
from models.api import CoubAPI
from widgets.handler import CoubletMouseEventHandler
from widgets.button import (CoubletButtonWidget,
                            ICON_AND_LABEL, LABEL_AND_ICON, HORIZONTAL, VERTICAL)

#------------------------------------------------------------------------------#
class CoubletWindowView(QWidget):

    SCROLL_POSITIVE = 30
    SCROLL_NEGATIVE = -SCROLL_POSITIVE

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, presenter, title):
        super().__init__(None)

        # Store static values
        self._presenter = presenter
        self._title = title.upper()
        self.setWindowTitle(title)

        self._buttons = []
        self._stream  = None

        # Build GUI
        self._build_gui()

        # Overload closing and scrolling event, and rename it just
        # for the sake of under-scored names ;)
        self.closeEvent = self.on_exit
        self.wheelEvent = self.on_mouse_scroll


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_exit(self, event):
        # Get current dimension and store in cache
        dim = self.geometry()
        CACHE['dimension'] = dim.x(), dim.y(), dim.width(), dim.height()
        # TODO: this call is at the wrong place
        CACHE.save()
        # Exit
        event.accept()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_mouse_scroll(self, event):
        # Get the "stregth" of scroll
        dy = event.pixelDelta().y()
        # If "hard" enoough downward
        if dy < self.SCROLL_NEGATIVE:
            if self._presenter.load_posts():
                print('[WINDOW] scroll: load')
        # If "hard" enough upward
        elif dy > self.SCROLL_POSITIVE:
            if self._presenter.sync_posts():
                print('[WINDOW] scroll: sync')

        # Kill posts in stream which are not visible
        # ??? Do this through window-presenter -> stream-presenter -> stream ???
        self._stream.reset_unseen_posts()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_menu_button_pressed(self, index):
        # Report event to presenter
        self._presenter.set_active_stream(index)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def remove_stream(self, index):
        # Set button deselected
        self._buttons[index].deselect()
        # Remove stream from layout
        self._posts.takeAt(1)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def set_stream(self, index, stream):
        # Set button selected
        self._buttons[index].select()
        # Indicate change in window title too
        self.setWindowTitle(
            '{} | {}'.format(self._title, CoubAPI.STREAM_NAMES[index].upper()))
        # Set stream to layout
        self._posts.insertLayout(1, stream)
        self._stream = stream


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _build_gui(self):
        # Storages
        buttons = self._buttons

        # Create layout for the entire application and zero-out
        self.layout = main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create and add scrollable area for streams
        posts = QScrollArea()
        posts.setWidgetResizable(True)
        posts.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        posts.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        posts.setFrameShape(QFrame.NoFrame)

        # Create a main-stream widget
        main_stream = QWidget()

        post_spacing = POST_SPACING_HEAD + POST_SPACING_TAIL

        # TODO: rename self._posts
        self._posts = posts_layout = QVBoxLayout()
        posts_layout.setSpacing(post_spacing)
        posts_layout.setContentsMargins(0, 0, 0, 0)

        # Add scroll-up icon and text
        posts_layout.addWidget(CoubletButtonWidget(icon=CONSTANTS['icon_scroll_up'],
                                                   label='SCROLL UP TO REFRESH',
                                                   font=CONSTANTS['text_font_generic'],
                                                   palette=CONSTANTS['text_color_light'],
                                                   order=ICON_AND_LABEL,
                                                   orientation=VERTICAL,
                                                   spacing=SMALL_PADDING,
                                                   padding_top=post_spacing),
                               alignment=Qt.AlignHCenter)
        # Dynamic space
        posts_layout.addStretch(0)
        # Add scroll-down icon and text
        posts_layout.addWidget(CoubletButtonWidget(icon=CONSTANTS['icon_scroll_down'],
                                                   label='SCROLL DOWN TO LOAD MORE',
                                                   font=CONSTANTS['text_font_generic'],
                                                   palette=CONSTANTS['text_color_light'],
                                                   order=LABEL_AND_ICON,
                                                   orientation=VERTICAL,
                                                   spacing=SMALL_PADDING,
                                                   padding_bottom=post_spacing),
                               alignment=Qt.AlignHCenter)

        # Set posts' layout to stream, add stream to main layout
        main_stream.setLayout(posts_layout)
        posts.setWidget(main_stream)
        main_layout.addWidget(posts)

        # Create menu-bar
        menu_bar = QWidget()
        menu_bar.setPalette(CONSTANTS['panel_color_darker'])
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
        menu_bar_layout.addSpacing(2*SMALL_PADDING)
        menu_bar_layout.addLayout(menu_buttons_layout)
        menu_bar_layout.addSpacing(2*SMALL_PADDING)

        # Assign layout and add menu-bar to app
        menu_bar.setLayout(menu_bar_layout)
        main_layout.addWidget(menu_bar)

        # Add buttons and spacess to menu-buttons layout
        menu_buttons_layout.addSpacing(2*SMALL_PADDING)
        # get default double-click interval
        for i, menu_item in enumerate(CoubAPI.STREAM_NAMES):
            # If not the first item, add
            # auto-stretching before it
            if i:
                menu_buttons_layout.addStretch(0)

            # Add menu item
            icon_name = 'icon_' + menu_item
            click = CoubletMouseEventHandler(l_single=lambda n=i: self.on_menu_button_pressed(n))
            menu_button = CoubletButtonWidget(icon=CONSTANTS[icon_name],
                                              icon_selected=CONSTANTS[icon_name + '_selected'],
                                              label=menu_item.upper(),
                                              order=ICON_AND_LABEL,
                                              orientation=HORIZONTAL,
                                              font=CONSTANTS['text_font_generic'],
                                              palette=CONSTANTS['text_color_light'],
                                              palette_selected=CONSTANTS['text_color_light_selected'],
                                              spacing=SMALL_PADDING,
                                              mouse_event_handler=click)
            buttons.append(menu_button)
            menu_buttons_layout.addWidget(menu_button)
        # Tail padding
        menu_buttons_layout.addSpacing(2*SMALL_PADDING)

        self.setLayout(main_layout)
        self.setPalette(CONSTANTS['panel_color_dark'])

        # Unpack dimension data
        x, y, width, height = CACHE['dimension']

        # If position have not been set before
        if x is NotImplemented:
            screen = QDesktopWidget().screenGeometry()
            x, y = (screen.width() - width) / 2, (screen.height() - height) / 2
        # Set window position and dimension
        self.setGeometry(x, y, width, height)
        self.setFixedWidth(width)
