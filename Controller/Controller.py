from Model import Server
from Model import Client
from socket import *
from struct import *
from _thread import *
import threading


class Controller:

    def __init__(self):
        self.ip_broadcast = '255.255.255.255'
        self.ip_unicast = gethostname()
        self.server_hostname = gethostname()
        self.server_port = 3117
        self.print_lock = threading.Lock()
        self.thread_list = []

    def init_servers(self, count=2):
        curr_thread = None
        for i in range(count):
            try:
                curr_thread = threading.Thread(target=self.threaded, args=(i+1,))
                self.thread_list.append(curr_thread)
                curr_thread.start()
            except Exception as e:
                print("Threads unexpected exception: ", e)
            finally:
                # curr_thread.join()
                print("done")

    def threaded(self, count):
        server = Server.Server(self.server_hostname, self.server_port, count)
        server.offer()

    def run_threads(self):
        for thread in self.thread_list:
            thread.start()

    def terminate_threads(self):
        for thread in self.thread_list:
            thread.join()

    def run_clients(self, s_hex, i_length):
        # client.request('abc4563fg', 6)
        # server_hostname = 'DESKTOP-TVPVUGN'
        client = Client.Client()
        if len(s_hex) != i_length or i_length > 40:
            print('type up to 40 characters of a hash to decode and verify length')
        else:
            s_stream = client.encode_message(s_hex)
            ans = client.discover()
            if ans is not None:
                client.request(s_stream)



