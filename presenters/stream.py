## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.95.221 (20141003)                       ##
##                                                                            ##
##                         File: presenters/stream.py                         ##
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

# Import Coublet modules
from views.stream import CoubletStreamView
from presenters.post import CoubletPostPresenter

#------------------------------------------------------------------------------#
class CoubletStreamPresenter:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, root, index, synchronisable):
        # Store static values
        self.synchronisable = synchronisable
        self._root = root
        self._stream = CoubletStreamView(self)

        # Set flags
        self.load_lock = False
        self.is_last_sync = False
        self._not_visited = True

        # Create storages
        self.scroll_bar_position = 0
        # TODO: is it possible to use an OrderedDict instead of this two ???
        self._post_presenters_by_order = []
        self._post_presenters_by_perma = {}


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def show_view(self):
        # If first time visit
        if self._not_visited:
            self._not_visited = False
            self._root.load_posts()
        # Show all posts this stream has
        for post_presenter in self._post_presenters_by_order:
            post_presenter.show_view()
        # If there is an on-going update
        if self.load_lock:
            # Indicate the stream is fetching data
            self._stream.show_loading(self.is_last_sync)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def hide_view(self):
        # Hide all posts this stream has
        for post_presenter in self._post_presenters_by_order:
            post_presenter.hide_view()
        # Hide loading indicator too
        self._stream.hide_loading()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def get_view(self):
        return self._stream


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def get_links(self):
        return self._post_presenters_by_perma.keys()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def push_loaded_posts(self, index, packet):
        # Get post-presenter by index
        post_presenter = self._post_presenters_by_order[self._insertion_index + index]
        # Push packet info to corresponding post-presenter
        post_presenter.load(packet)
        # Store presenter by perma-link
        self._post_presenters_by_perma[packet['perma']] = post_presenter


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def push_loaded_updates(self, packet):
        # TODO: can this ever raise KeyError ???
        self._post_presenters_by_perma[packet['perma']].update(packet)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def show_loading(self, sync):
        # Indicate the stream is fetching data
        self._stream.show_loading(sync)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def no_more_data(self):
        # TODO: create a nice icon for this and inform user about it...
        print('[STREAM] you have reached the end of the world - no more posts left')


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def record_index(self, sync):
        # At first call of a loading-session store the insertion index
        self._insertion_index = 0 if sync else len(self._post_presenters_by_order)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def schedule_posts(self, count, sync):
        # Indicate all data has been fetched
        self._stream.hide_loading()
        # If new posts scheduled
        if count:
            # Get local reference
            post_presenters = self._post_presenters_by_order
            # If insert post
            if sync:
                store_presenter = lambda p: post_presenters.insert(0, p)
                add_to_stream = self._stream.insert_post
            # If append post
            else:
                store_presenter = post_presenters.append
                add_to_stream = self._stream.append_post
            # Create posts and add them to
            for _ in range(count):
                post = CoubletPostPresenter(self)
                store_presenter(post)
                add_to_stream(post.get_view())


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def reset_unseen_posts(self):
        # Kill posts in stream which are not visible
        for post_presenter in self._post_presenters_by_order:
            post_presenter.reset_unseen()

