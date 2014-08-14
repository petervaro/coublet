## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.172 (20140814)                       ##
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
from PyQt5.QtWidgets import (QWidget,
                             QFrame,
                             QHBoxLayout,
                             QVBoxLayout,
                             QScrollArea,
                             QDesktopWidget)

# Import Coublet modules
from views.vars import *
from models.cache import CACHE
from models.api import CoubAPI
from widgets.handler import CoubletMouseEventHandler
from widgets.button import (CoubletButtonWidget,
                            VERTICAL,
                            HORIZONTAL,
                            ICON_AND_LABEL,
                            LABEL_AND_ICON)

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
            self._presenter.load_posts()
        # If "hard" enough upward
        elif dy > self.SCROLL_POSITIVE:
            self._presenter.sync_posts()

        # Kill posts in stream which are not visible
        self._presenter.reset_unseen_posts()


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
    def get_scroll_position(self):
        # Get position of scroll bar
        return self._scroll_area.verticalScrollBar().sliderPosition()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def set_scroll_position(self, value):
        # Set position of scroll bar
        self._scroll_area.verticalScrollBar().setSliderPosition(value)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def show_scroll_indicators(self, up=False, down=False):
        # Place scroll indicators
        up_space = down_space = POST_SPACING_FULL
        if up:
            self._scroll_up.show()
            up_space = 0
        if down:
            self._scroll_down.show()
            down_space = 0
        # Set leading and trailing padding
        self._posts.setContentsMargins(0, up_space, 0, down_space)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def hide_scroll_indicators(self, up=False, down=False):
        # Remove scroll indicators
        up_space = down_space = 0
        if up:
            self._scroll_up.hide()
            up_space = POST_SPACING_FULL
        if down:
            self._scroll_down.hide()
            down_space = POST_SPACING_FULL
        # Set leading and trailing padding
        self._posts.setContentsMargins(0, up_space, 0, down_space)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _build_gui(self):
        # Storages
        buttons = self._buttons

        # Unpack dimension data
        x, y, width, height = CACHE['dimension']

        # If position have not been set before
        if x is NotImplemented:
            screen = QDesktopWidget().screenGeometry()
            x, y = (screen.width() - width) / 2, (screen.height() - height) / 2
        # Set window position and dimension
        self.setGeometry(x, y, width, height)
        self.setFixedWidth(width)

        # Create layout for the entire application and zero-out
        self.layout = main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create and add scrollable area for streams
        self._scroll_area = posts = QScrollArea()
        posts.setWidgetResizable(True)
        posts.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        posts.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        posts.setFrameShape(QFrame.NoFrame)

        # Create a main-stream widget
        main_stream = QWidget()
        main_stream.setFixedWidth(width)

        # TODO: rename self._posts to something meaningful
        self._posts = posts_layout = QVBoxLayout()
        posts_layout.setSpacing(POST_SPACING_FULL)
        posts_layout.setContentsMargins(0, 0, 0, 0)

        # HACK: in both scroll arrows the 'padding_left' value is a hack.
        #       The reason why the arrows are not aligned to the horizontal
        #       center is unknown as it looks like everything is set up properly

        # Add scroll-up icon and text
        self._scroll_up = CoubletButtonWidget(icon=CONSTANTS['icon_scroll_up'],
                                              label='SCROLL UP TO REFRESH',
                                              font=CONSTANTS['text_font_generic'],
                                              palette=CONSTANTS['text_color_light'],
                                              order=ICON_AND_LABEL,
                                              orientation=VERTICAL,
                                              spacing=SMALL_PADDING,
                                              padding_top=POST_SPACING_FULL,
                                              padding_left=8)
        posts_layout.addWidget(self._scroll_up, alignment=Qt.AlignHCenter)
        # Dynamic space
        posts_layout.addStretch(0)
        # Add scroll-down icon and text
        self._scroll_down = CoubletButtonWidget(icon=CONSTANTS['icon_scroll_down'],
                                                label='SCROLL DOWN TO LOAD MORE',
                                                font=CONSTANTS['text_font_generic'],
                                                palette=CONSTANTS['text_color_light'],
                                                order=LABEL_AND_ICON,
                                                orientation=VERTICAL,
                                                spacing=SMALL_PADDING,
                                                padding_bottom=POST_SPACING_FULL,
                                                padding_left=8)
        posts_layout.addWidget(self._scroll_down, alignment=Qt.AlignHCenter)

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
