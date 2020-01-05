import logging
import hashlib
import threading
from re import split
from socket import *
from struct import *
from Model import Config
from Model import Cracker


class Server:

    mutex_clients = threading.Lock()
    d_clients = {}
    list_threads = []
    server_socket = None

    def __init__(self, hostname=gethostname(), port=3117, server_id=0):
        self.ip_broadcast = '255.255.255.255'
        self.ip_unicast = ''
        self.server_hostname = hostname
        self.server_port = port
        self.hash_lib = hashlib.sha1()
        self.server_id = server_id
        self.config = Config.Config()
        self.config.set_team_name()
        self.config.set_hash_input('422ab519eac585ef4ab0769be5c019754f95e8dc')
        self.config.set_hash_length('6')
        self.cracker = Cracker.Cracker()

    def init_servers(self):
        self.server_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        # self.server_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        self.server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        # self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind((self.server_hostname, self.server_port))
        # self.server_socket.listen(5)  # queue up to 5 connection requests before refusing outside connections
        # self.server_socket.listen(1)
        # self.server_socket.settimeout(0.2)  # Set a timeout so the socket does not block when trying to receive data.
        print('Server No. ', self.server_id, ': Socket is listening')
        self.d_clients = {}
        flag = self.offer()  # callback function
        # this_server_address = self.offer_with_accept()  # callback function
        self.print_dict()
        print('Server: ', self.server_id, 'Done offering with client')
        if flag:
            self.ack()
        else:
            print('Server cant start ack')

    def offer(self):
        while True:
            try:
                print('(offer) Server No. ', self.server_id, ': Still waiting for a client DISCOVER')
                self.mutex_clients.acquire()  # lock acquired to avoid client collision
                s_stream, client_address = self.server_socket.recvfrom(2048)  # callback function
                message = self.config.decode_message(s_stream)
                # print('(offer) Server No. ', self.server_id, ': Received a message: ', message)
                print('(offer) Server No. ', self.server_id, ': Received a message from a client')
                d_message = self.config.get_decoded_message_to_dict(message)
                # self.config.print_dict(d_message)
                # if message == self.config.discover:
                if d_message['transfer_type'] == self.config.discover:
                    self.d_clients[str(self.server_id)] = client_address[1]
                    # server_info = self.tuple_to_string(self.server_socket.getsockname())
                    # message = self.config.encode_message(server_info)
                    message = self.config.get_data_ready_to_transfer(self.config.offer)
                    self.server_socket.sendto(message, client_address)
                    self.mutex_clients.release()
                    return True
                else:
                    print('(offer) Server still waiting for client request')
                    self.mutex_clients.release()
            except Exception as e:
                # self.mutex_clients.release()  # lock released on exit
                print('oops offer exception: ', e)
                # self.server_socket.close()
                # client_address.close()
                return False

    def ack(self):
        while True:
            try:
                print('(ack) Server No. ', self.server_id, ': Still waiting for a client REQUEST')
                self.mutex_clients.acquire()
                s_stream, client_address = self.server_socket.recvfrom(2048)  # any available port in the client
                message = self.config.decode_message(s_stream)
                self.config.set_original_string_start('aaa')
                self.config.set_original_string_end('zzz')
                d_message = self.config.get_decoded_message_to_dict(message)
                print('(ack) Server No. ', self.server_id, ': Received a message from a client')
                # if message:
                if d_message['transfer_type'] == self.config.request:
                    # s_hex = self.decode_hash(message, 'aaazzz')
                    # ans = self.config.encode_message(s_hex)
                    print('(ack) Server found hash')
                    ans = self.config.encode_message('ans harta barta')
                    self.server_socket.sendto(ans, client_address)
                    self.mutex_clients.release()
                    self.server_socket.close()
                    # client_address.close()
                    return True
                else:
                    print('Server still waiting for client request')
                    self.mutex_clients.release()
            except Exception as e:
                print('oops ack exception: ', e)
                # self.mutex_clients.release()
                # self.server_socket.close()
                # client_address.close()
                return False

    def tuple_to_string(self, tup):
        s_host = ''.join(tup[0])
        s_port = ''.join(str(tup[1]))
        return s_host + ':' + s_port

    def decode_hash(self, s_coded_value, range):
        decoded_value = 'Here we calculate'
        print(decoded_value)
        return decoded_value

    def print_dict(self):
        for key, value in self.d_clients.items():
            print('-Server Map- Server No.: ', key, ', Client No.: ', value)

    def init_threads(self, count=2):
        for i in range(count):
            try:
                curr_thread = threading.Thread(target=self.threaded, args=(self.server_hostname, self.server_port, i+1))
                self.list_threads.append(curr_thread)
                # curr_thread.start()
            except Exception as e:
                print("Threads unexpected exception: ", e)
            finally:
                # curr_thread.join()
                # print("done, Threads joined")
                print('done initializing thread number: ', i+1)
        self.run_threads()
        self.terminate_threads()

    def threaded(self, server_hostname, server_port, thread_count):
        server = Server(server_hostname, server_port, thread_count)
        server.init_servers()
        # flag = server.offer()
        # flag = server.offer_with_accept()

    def run_threads(self):
        for thread in self.list_threads:
            thread.start()

    def terminate_threads(self):
        for thread in self.list_threads:
            thread.join()


# with threads #
server_manager = Server()
server_manager.init_threads(2)

# no threads #
"""
server_hostname = gethostname()
server_port = 3117
server = Server(server_hostname, server_port, 1)
flag = server.offer()
if flag:
    server.ack()
else:
    print('Server cant start ack')
"""
