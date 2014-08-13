## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.049 (20140813)                       ##
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
class CoubletEmptyQueue(Exception): pass
class CoubletNoMoreDataToFetch(Exception): pass

#------------------------------------------------------------------------------#
class CoubletAppModel:

    PAGE = 5

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self):
        # Create an API reference
        self._api = CoubAPI(self.PAGE)

        # Set storages
        self._load_counters   = load_counters   = []
        self._sync_counters   = sync_counters   = []
        self._packets_queues  = packets_queues  = []
        self._raw_data_queues = raw_data_queues = []
        self._schedule_counts = schedule_counts = []
        self._packet_ids      = packet_ids      = []

        # Set values and storages for each stream
        for stream in CoubAPI.STREAM_NAMES:
            # Create counters as: total pages, curent_pages
            load_counters.append([1, 1])
            sync_counters.append([1, 1])
            # Create queues for each stream
            raw_data_queues.append(queue.Queue())
            packets_queues.append(queue.Queue())
            # Create currently loading packet counter
            schedule_counts.append(0)
            # Store packet IDs per stream
            packet_ids.append(set())

        # CONNECTION ERROR, or any ERROR => what is it going to do?

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load(self, index, sync):
        # If synchronising stream
        if sync:
            total, current = self._sync_counters[index]
        # If loading more content to stream
        else:
            total, current = self._load_counters[index]

        # If there is more content to load
        if current <= total:
            self._api.fetch_data_to_queue(index, current, self._raw_data_queues[index])
            # Reset schedule counter
            self._schedule_counts[index] = 0
        # If reached end of stream
        else:
            raise CoubletNoMoreDataToFetch


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def reset_sync(self, index):
        self._sync_counters[index] = [1, 1]


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
            packets_queue = self._packets_queues[index]
            packet_ids = self._packet_ids[index]

            # Number of packets will be scheduled
            packet_count = 0
            # Temporary storage for files
            files = set()
            # Get folder paths of local files
            video_path, thumb_path, avatar_path = CACHE['folders']

            # Process each packet
            for i, packet in enumerate(packets):
                # Get unique packet ID
                id = packet['id']
                # If synchronising stream and ID is already in the stream
                if sync and id in packet_ids:
                    continue
                # If either not syncronising or ID is nor in the stream
                packet_ids.add(id)
                # Increase number of packets
                packet_count += 1

                # Create video file path and store it in temporary files
                video_file = os.path.join(video_path, id + '.mp4')
                files.add(video_file)

                # Create thumbnail file path and store it in temporary files
                thumb_file = os.path.join(thumb_path, id + '.jpg')
                files.add(video_file)

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
                    CoubletDownloadPacketThread(i, packet, packets_queue).start()
                # If cached, pushed it to queue
                else:
                    packets_queue.put((i, packet))

            # Store files
            CACHE['temporary'].update(files)
            # Store and return number of scheduled packets
            self._schedule_counts[index] += packet_count
            return self._schedule_counts[index]
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
            self._schedule_counts[index] -= 1
            # Return counter and packet
            return self._schedule_counts[index], indexed_packet
        # If packet data not downloaded
        except queue.Empty:
            raise CoubletEmptyQueue
