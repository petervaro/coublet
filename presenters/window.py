## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.95.237 (20141003)                       ##
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
from models.com import CoubletConnectionError
from presenters.stream import CoubletStreamPresenter
from models.app import (CoubletSyncMore,
                        CoubletEmptyQueue,
                        CoubletNothingScheduled,
                        CoubletNoMoreDataToFetch)


#------------------------------------------------------------------------------#
class CoubletWindowPresenter:

    RECONNECT   = 10000
    AUTO_SAVE   = 40000
    AUTO_SYNC   = 60000
    AUTO_UPDATE = 90000
    SCHEDULED_CALL = 300

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, app_model, app_name, *args, **kwargs):
        # Set static values
        self._app = app_model
        self._window = CoubletWindowView(self, app_name)

        # Set up auto-sync timer
        self._auto_sync = QTimer()
        self._auto_sync.setInterval(self.AUTO_SYNC)
        self._auto_sync.timeout.connect(self.sync_posts)

        # Set up auto-update timer
        self._auto_update = QTimer()
        self._auto_update.setInterval(self.AUTO_UPDATE)
        self._auto_update.timeout.connect(self.update_posts)

        # Create stream presenters and first-call flags storage
        self._first_calls = first_calls = []
        self._stream_presenters = stream_presenters = []
        for i, has_sync in enumerate(CoubAPI.STREAM_SYNCS):
            stream_presenters.append(CoubletStreamPresenter(self, i, has_sync))
            first_calls.append(True)

        # Load first stream
        self._active_stream_index = 0
        first_stream = self._stream_presenters[0]
        self._window.set_stream(0, first_stream.get_view())
        first_stream.show_view()

        # Start timers
        self._auto_sync.start()
        self._auto_update.start()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def show_view(self):
        self._window.show()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def hide_view(self):
        self._window.hide()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def set_auto_save(self, callback):
        # These are here and not in the constructor, because CACHE file is only
        # available for CoubletApp, which is not available from CoubletAppModel
        # nor from this (CoubletWindowPresenter) -- that's because all QTimer
        # calls should happen in the CoubletApp presenter...
        # TODO: consider redesigning object hierarchy => should this presenter
        #       have to start the auto-save call chain?
        self._auto_save = QTimer()
        self._auto_save.setInterval(self.AUTO_SAVE)
        self._auto_save.timeout.connect(callback)
        self._auto_save.start()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def set_active_stream(self, index):
        # If selected stream is not active yet
        if index != self._active_stream_index:
            window = self._window
            # Remove old stream
            old_index = self._active_stream_index
            old_stream = self._stream_presenters[old_index]
            old_stream.scroll_bar_position = window.get_scroll_position()
            old_stream.hide_view()
            old_stream.reset_unseen_posts()
            window.remove_stream(old_index)
            window.hide_scroll_indicators(True, False)
            # Load new stream
            self._active_stream_index = index
            new_stream = self._stream_presenters[index]
            window.set_stream(index, new_stream.get_view())
            new_stream.show_view()
            window.set_scroll_position(new_stream.scroll_bar_position)
            window.show_scroll_indicators(CoubAPI.STREAM_SYNCS[index], True)
            self._auto_sync.start()
            return True
        # If selected stream is already active
        return False


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load_posts(self):
        index = self._active_stream_index
        # If there is no on going loading
        if not self._stream_presenters[index].load_lock:
            self._first_calls[index] = True
            self._get_posts(index, sync=False)
            return True
        # If stream is already loading posts
        return False


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def sync_posts(self):
        index = self._active_stream_index
        # If there is no on going loading
        stream_presenter = self._stream_presenters[index]
        if not stream_presenter.load_lock and stream_presenter.synchronisable:
            self._first_calls[index] = True
            self._get_posts(index, sync=True)
            return True
        # If stream is already loading posts
        return False


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def update_posts(self):
        index = self._active_stream_index

        # Start downloading updates
        self._app.update(index, self._stream_presenters[index].get_links())
        # Start pushing updates
        self._push_updates(index)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def reset_unseen_posts(self):
        # Kill posts in stream which are not visible
        self._stream_presenters[self._active_stream_index].reset_unseen_posts()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _get_posts(self, index, sync):
        # Get currently active stream
        index = self._active_stream_index
        # Lock further
        stream_presenter = self._stream_presenters[index]
        stream_presenter.load_lock = True
        stream_presenter.is_last_sync = sync
        # If there is data to download
        try:
            # Start downloading posts
            self._app.load(index, sync, self._first_calls[index])
            stream_presenter.record_index(sync)
            stream_presenter.show_loading(sync)
        # If there is no data to download
        except CoubletNoMoreDataToFetch:
            stream_presenter.load_lock = False
            stream_presenter.no_more_data()
            return
        # Pull posts from model and push it to view
        QTimer.singleShot(0, lambda: self._pull_posts(index, sync))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _pull_posts(self, index, sync):
        # If raw_data already in the queue
        try:
            # Translate raw data and download necessary files
            packet_count = self._app.pull_raw_data(index, sync)
            # Prepare stream for posts
            self._stream_presenters[index].schedule_posts(packet_count, sync)
            # Start pushing posts to stream
            QTimer.singleShot(0, lambda: self._push_posts(index, sync))
        # If queue is empty
        except CoubletEmptyQueue:
            # Try pulling packets later
            QTimer.singleShot(self.SCHEDULED_CALL, lambda: self._pull_posts(index, sync))
        # If there could be more
        except CoubletSyncMore:
            # Try to load more posts
            self._first_calls[index] = False
            QTimer.singleShot(0, lambda: self._get_posts(index, sync))
        # If there were a problem during the JSON data loading
        except CoubletConnectionError:
            QTimer.singleShot(self.RECONNECT, lambda: self._get_posts(index, sync))
            # TODO: add some sort of connection counter and give up
            #       at some point, and indicate this to the user
            print('Reconnecting, as there was a problem during fetching ...')


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _push_posts(self, index, sync):
        # If packets already in the queue
        try:
            # Pull from queue and push to stream as many packets as possible
            while True:
                self._stream_presenters[index].push_loaded_posts(*self._app.pull_packets(index))
        # If queue is empty but packets were scheduled
        except CoubletEmptyQueue:
            # Try pulling packets later
            QTimer.singleShot(self.SCHEDULED_CALL, lambda: self._push_posts(index, sync))
        # If queue is empty and no packets were scheduled
        except CoubletNothingScheduled:
            print('Thread is finished.')
            # Release stream
            self._stream_presenters[index].load_lock = False


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _push_updates(self, index):
        # If packets already in the queue
        try:
            # Pull as many packates as possible from the queue
            while True:
                self._stream_presenters[index].push_loaded_updates(self._app.pull_updates(index))
        # If queue is empty but packets were scheduled
        except CoubletEmptyQueue:
            # Try pulling packets later
            QTimer.singleShot(self.SCHEDULED_CALL, lambda: self._push_updates(index))
        # If there was a problem during the JSON data loading
        except CoubletConnectionError:
            QTimer.singleShot(self.RECONNECT, lambda: self._push_updates(index))
            print('[ ERROR ] _push_updates(): handled')
        # If queue is empty and no packates scheduled
        except CoubletNothingScheduled:
            print('All posts are updated.')
