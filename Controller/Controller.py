import hashlib

from Model import SocketManager
from Model import Server
from Model import Client
from Model import Cracker
import threading

from Model.test import sha1


class Controller:

    cracker = None

    def __init__(self):

        self.mutex = threading.Lock()
        self.thread_list = []
        self.d_bytes_structure = {
            'team_name': 32,
            'transfer_type': 1,
            'hash_input': 40,
            'original_length': 1,
            'original_string_start': 256,
            'original_string_end': 256,
        }
        self._socket_manager = SocketManager.SocketManager()
        # server_hostname = 'DESKTOP-TVPVUGN'

    def run_server(self, team_name, hash_input, hash_length, server_count):
        self._socket_manager.set_configurations(team_name, hash_input, hash_length, server_count)
        # self._socket_manager.init_cracker()

        # servers with threads #
        server_manager = Server.Server(self._socket_manager)
        server_manager.init_server_threads(server_count)

    def run_client(self, team_name, hash_input, hash_length, client_count=1):
        self._socket_manager.set_configurations(team_name, hash_input, hash_length, client_count)
        # self._socket_manager.init_cracker()

        client = Client.Client(self._socket_manager)
        client.discover(self._socket_manager.server_count)
        client.request()

    def run_threaded_app(self, team_name, hash_input, hash_length, server_count):
        self._socket_manager.set_configurations(team_name, hash_input, hash_length, server_count)
        try:
            threading.Thread(target=self.threaded_server, args=(server_count,)).start()
            threading.Thread(target=self.threaded_client, args=()).start()
        except Exception as e:
            print("Threads unexpected exception: ", e)
        finally:
            print("done")

    def threaded_server(self, server_count):
        server_manager = Server.Server(self._socket_manager)
        server_manager.init_server_threads(server_count)

    def threaded_client(self):
        client = Client.Client(self._socket_manager)
        client.discover(self._socket_manager.server_count)
        client.request()

    def check_fill_stream(self, message, key_name):
        other_length = len(message)
        this_length = self.d_bytes_structure[key_name]
        s_this_length = str(this_length)
        if other_length < this_length:
            s_format = "{:<" + s_this_length + "}"
            corrected_message = s_format.format(message)
            print('Input is short by ', this_length-other_length, ' characters')
            print('Corrected to: ' + corrected_message)
            return corrected_message
        elif other_length > this_length:
            corrected_message = message[0:this_length+1]
            print('Input is long by ', other_length-this_length, ' characters')
            print('Corrected to: ' + corrected_message)
            return corrected_message
        else:
            return message
