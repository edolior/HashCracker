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
        self.team_name_length = 32
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

