## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.95.223 (20141003)                       ##
##                                                                            ##
##                            File: models/app.py                             ##
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

# Import Coublet modules
from models.api import CoubAPI
from models.cache import CACHE
from models.com import CoubletDownloadPacketThread

#------------------------------------------------------------------------------#
class CoubletSyncMore(Exception): pass
class CoubletEmptyQueue(Exception): pass
class CoubletNothingScheduled(Exception): pass
class CoubletNoMoreDataToFetch(Exception): pass

#------------------------------------------------------------------------------#
class CoubletAppModel:

    PAGE = 5

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self):
        # Create an API reference
        self._api = CoubAPI(self.PAGE)


        # Set storages
        self._load_counters          = load_counters          = []
        self._sync_counters          = sync_counters          = []
        self._packets_queues         = packets_queues         = []
        self._raw_data_queues        = raw_data_queues        = []
        self._raw_update_queues      = raw_update_queues      = []
        self._scheduled_data_count   = scheduled_data_count   = []
        self._scheduled_update_count = scheduled_update_count = []
        self._packet_ids             = packet_ids             = []

        # Set values and storages for each stream
        for stream in CoubAPI.STREAM_NAMES:
            # Create counters as: total pages, curent_pages
            load_counters.append([1, 1])
            sync_counters.append([1, 1])
            # Create queues for each stream
            raw_data_queues.append(queue.Queue())
            raw_update_queues.append(queue.Queue())
            packets_queues.append(queue.Queue())
            # Create currently loading packet counter
            scheduled_data_count.append(0)
            scheduled_update_count.append(0)
            # Store packet IDs per stream
            packet_ids.append(set())


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load(self, index, sync, first_call):
        # If synchronising stream
        if sync:
            total, current = self._sync_counters[index]
        # If loading more content to stream
        else:
            total, current = self._load_counters[index]

        # If there is more content to load
        if current <= total:
            # Start fetching data
            self._api.fetch_data_to_queue(index, current, self._raw_data_queues[index])
            # If this call is not part of a call-sequence
            if first_call:
                # Reset schedule counter
                self._scheduled_data_count[index] = 0
        # If reached end of stream
        else:
            raise CoubletNoMoreDataToFetch


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def update(self, index, links):
        # Increase schedule counter
        self._scheduled_update_count[index] = len(links)
        # Start downloading data of the given perma-links
        raw_update_queue = self._raw_update_queues[index]
        for link in links:
            self._api.fetch_update_to_queue(link, raw_update_queue)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def pull_raw_data(self, index, sync):
        # If JSON data downloaded
        try:
            # Translate packets, and store them
            total_pages, packets = self._api.translate_fetched_data(
                self._raw_data_queues[index].get_nowait())

            # Update counter values
            counter = (self._sync_counters if sync else self._load_counters)[index]
            counter[0] = total_pages
            counter[1] += 1

            # Get local references
            packet_ids = self._packet_ids[index]
            packets_queue = self._packets_queues[index]

            # Number of packets will be scheduled
            packet_count = 0
            packet_index = self._scheduled_data_count[index]
            # Temporary storage for files
            files = set()
            # Get folder paths of local files
            video_path, thumb_path, avatar_path = CACHE['folders']

            # Process each packet
            for packet in packets:
                # Get unique packet ID
                id = packet['id']
                # If ID is already in the stream
                if id in packet_ids:
                    continue
                # If either not syncronising or ID is not in the stream
                packet_ids.add(id)

                # Create video file path and store it in temporary files
                video_file = os.path.join(video_path, id + '.mp4')
                files.add(video_file)

                # Create thumbnail file path and store it in temporary files
                thumb_file = os.path.join(thumb_path, id + '.jpg')
                files.add(thumb_file)

                # Create avatar file path and store it in temporary files
                avatar_url = packet['user'][0]
                if avatar_url:
                    ext = os.path.splitext(avatar_url)[1]
                    user_file = os.path.join(avatar_path, packet['user_id'] + ext)
                    files.add(user_file)
                else:
                    user_file = None

                # Add file names to packet
                packet['video'].append(video_file)
                packet['thumb'].append(thumb_file)
                packet['user'].append(user_file)

                # If video file not already cached then
                # download it and push it to the queue
                if not os.path.isfile(video_file):
                    CoubletDownloadPacketThread(packet_index, packet, packets_queue).start()
                # If cached, pushed it to queue
                else:
                    packets_queue.put((packet_index, packet))

                # Increase number of packets and index
                packet_count += 1
                packet_index += 1

            # Store files
            CACHE['temporary'].update(files)

            # If syncronising and
            if sync:
                # If loaded maximum number of packets per page
                if packet_count == self.PAGE:
                    # Increase schedule count
                    self._scheduled_data_count[index] += packet_count
                    # Indicate queue is not ready yet
                    raise CoubletSyncMore
                # If number of packets is less than maximum
                else:
                    # Calculate total number of packets
                    packet_count += self._scheduled_data_count[index]
                    # Reset sync counter
                    self._sync_counters[index] = [1, 1]
            # If regular loading
            else:
                # If number of loaded packets are less the preferred
                # TODO: but what if there are no more posts left?
                if packet_count < self.PAGE:
                    # Increase schedule count
                    self._scheduled_data_count[index] += packet_count
                    # Indicate queue is not ready yet
                    raise CoubletSyncMore
                # If number of packets is equal to preferred
                else:
                    # Calculate total number of packets
                    packet_count += self._scheduled_data_count[index]

            # Store scheduled packet counts
            self._scheduled_data_count[index] = packet_count
            # Store and return number of scheduled packets
            return packet_count
        # If JSON data not downloaded
        except queue.Empty:
            raise CoubletEmptyQueue


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def pull_packets(self, index):
        # If packet data downloaded
        try:
            # Get next packet from queue and update schedule counter
            indexed_packet = self._packets_queues[index].get_nowait()
            # Decrease schedule counter
            self._scheduled_data_count[index] -= 1
            # Return counter and packet
            return indexed_packet
        # If packet data not downloaded
        except queue.Empty:
            # If packet scheduled but not yet arrived
            if self._scheduled_data_count[index]:
                raise CoubletEmptyQueue
            # If nothing scheduled
            raise CoubletNothingScheduled


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def pull_updates(self, index):
        try:
            # Translate raw data into packet
            packet = self._api.translate_fetched_update(
                        self._raw_update_queues[index].get_nowait())
            # Decrease schedule counter
            self._scheduled_update_count[index] -= 1
            # Return packet
            return packet
        # If JSON data not downloaded
        except queue.Empty:
            # If update scheduled but not yet arrived
            if self._scheduled_update_count[index]:
                raise CoubletEmptyQueue
            # If nothing scheduled
            raise CoubletNothingScheduled
