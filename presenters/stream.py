## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.054 (20140813)                       ##
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
    def __init__(self, root, index):
        # Store static values
        self._root = root
        self._stream = CoubletStreamView(self, index)

        # Set flags
        self._not_visited = True
        self.load_lock = False

        # Create storages
        self._post_presenters = []


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def show_view(self):
        # If first time visit
        if self._not_visited:
            self._root.load_posts()
        # Show all posts this stream has
        for post_presenter in self._post_presenters:
            post_presenters.show_view()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def hide_view(self):
        # Hide all posts this stream has
        for post_presenter in self._post_presenters:
            post_presenter.hide_view()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def get_view(self):
        return self._stream


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def push_loaded_posts(self, index, packet):
        # Push packet info to corresponding post
        self._post_presenters[self._insertion_index + index].load(packet)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def show_loading(self, sync):
        # Indicate the stream is fetching data
        self._stream.show_loading(sync)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def no_more_data(self):
        # TODO: create a nice icon for this and inform user about it...
        print('[STREAM] you have reached the end of the world - no more posts')


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def schedule_posts(self, count, sync):
        # Indicate all data has been fetched
        self._stream.hide_loading()
        # If new posts scheduled
        if count:
            # Get local reference
            post_presenters = self._post_presenters
            # If insert post
            if sync:
                self._insertion_index = 0
                add_to_stream = self._stream.insert_post
            # If append post
            else:
                self._insertion_index = len(post_presenters)
                add_to_stream = self._stream.append_post
            # Create posts and add them to
            for _ in range(count):
                post = CoubletPostPresenter(self)
                post_presenters.append(post)
                add_to_stream(post.get_view())
