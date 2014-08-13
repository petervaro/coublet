## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.054 (20140813)                       ##
##                                                                            ##
##                         File: presenters/window.py                         ##
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
import queue

# Import PyQt5 modules
from PyQt5.QtCore import QTimer

# Import Coublet modules
from models.api import CoubAPI
from views.window import CoubletWindowView
from presenters.stream import CoubletStreamPresenter
from models.app import CoubletEmptyQueue, CoubletNoMoreDataToFetch

#------------------------------------------------------------------------------#
class CoubletWindowPresenter:

    REFRESH = 300

    # FIXME: SOME STREAM HAS SCROLL-UP-TO-REFRESH SOME DOESN'T (RANDOM)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, app_model, app_name, *args, **kwargs):
        self._app = app_model
        self._window = CoubletWindowView(self, app_name)

        # Create stream presenters
        self._stream_presenters = stream_presenters = []
        for i, stream_name in enumerate(CoubAPI.STREAM_NAMES):
            stream_presenters.append(CoubletStreamPresenter(self, i))

        # Load first stream
        self._active_stream_index = 0
        first_stream = self._stream_presenters[0]
        self._window.set_stream(0, first_stream.get_view())
        first_stream.show_view()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def show_view(self):
        self._window.show()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def hide_view(self):
        self._window.hide()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def set_active_stream(self, index):
        # If selected stream is not active yet
        if index != self._active_stream_index:
            # Remove old stream
            old_index = self._active_stream_index
            self._stream_presenters[old_index].hide_view()
            self._window.remove_stream(old_index)
            # Load new stream
            self._active_stream_index = index
            new_stream = self._stream_presenters[index]
            self._window.set_stream(index, new_stream.get_view())
            new_stream.show_view()
            return True
        # If selected stream is already active
        return False


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load_posts(self):
        index = self._active_stream_index
        # If there is no on going loading
        if not self._stream_presenters[index].load_lock:
            # Convenient wrapper
            self._get_posts(index, sync=False)
            return True
        # If stream is already loading posts
        return False


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def sync_posts(self):
        index = self._active_stream_index
        # If there is no on going loading
        if not self._stream_presenters[index].load_lock:
            self._get_posts(index, sync=True)
            return True
        # If stream is already loading posts
        return False


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _get_posts(self, index, sync):
        # Get currently active stream
        index = self._active_stream_index
        # Lock further
        stream_presenter = self._stream_presenters[index]
        stream_presenter.load_lock = True
        # If there is data to download
        try:
            # Start downloading posts
            self._app.load(index, sync)
            stream_presenter.show_loading(sync)
        # If there is no data to download
        except CoubletNoMoreDataToFetch:
            stream_presenters.load_lock = False
            stream_presenters.no_more_data()
            return
        # Pull posts from model and push it to view
        self._pull_posts(index, sync)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _pull_posts(self, index, sync):
        # If raw_data already in the queue
        try:
            # Translate raw data and download necessary files
            packet_count = self._app.pull_raw_data(index, sync)
            # If synchronising stream
            if sync:
                # If there is more data
                if packet_count:
                    # Try to load even more data
                    self._get_posts(index, sync)
                # If stream is up-to-date
                else:
                    # Reset sync-counter
                    self._app.reset_sync(index)
            # Prepare stream for posts
            self._stream_presenters[index].schedule_posts(packet_count, sync)
            # Start pushing posts to stream
            self._push_posts(index)
        # If queue is empty
        except CoubletEmptyQueue:
            QTimer.singleShot(self.REFRESH, lambda i=index, s=sync: self._pull_posts(i, s))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _push_posts(self, index):
        # If packets already in the queue
        try:
            # Load as may packets as possible
            while True:
                # Pull a packet from
                is_more, indexed_packet = self._app.pull_packets(index)
                self._stream_presenters[index].push_loaded_posts(*indexed_packet)
                # If there is no more scheduled packet
                if not is_more:
                    # Release load-lock
                    self._stream_presenters[index].load_lock = False
                    return
        # If queue is empty
        except CoubletEmptyQueue:
            QTimer.singleShot(self.REFRESH, lambda i=index: self._push_posts(i))
