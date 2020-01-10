import hashlib
import threading
from socket import *
import SocketManager
import Ranger
import Cracker
import time


class Server:

    mutex_clients = threading.Lock()
    d_clients = {}
    list_threads = []
    server_socket = None
    cracker = None

    def __init__(self, ref_socket_manager, server_id=0):
        self._socket_manager = ref_socket_manager
        self.server_id = server_id

    def init_servers(self):
        self.init_sockets()
        self.offer()

    def init_sockets(self):
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', int(self._socket_manager.server_port)))
        self.server_socket.settimeout(15)  # Set a timeout so the socket does not block when trying to receive data.
        # self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        # self.server_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)  # Enables UDP
        # self.server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # Enable broadcasting mode
        # self.server_socket.listen(5)  # queue up to 5 connection requests before refusing outside connections
        print('Server No. ', self.server_id, ': Socket is listening')

    def offer(self):
        while True:
            try:
                print('(offer) Server No. ', self.server_id, ': Waiting for a client DISCOVER')
                try:
                    s_stream, client_address = self.server_socket.recvfrom(2048)  # callback function
                except timeout:
                    print('(offer) Server No. ', self.server_id, ' Server waited too long for client. Try again Later...')
                    break
                d_message = self._socket_manager.decode_message(s_stream)
                print('(offer) Server No. ', self.server_id, ': Received a message from a client: ', d_message['transfer_type'])
                if d_message['transfer_type'] == self._socket_manager.discover:
                    self.d_clients[str(self.server_id)] = client_address[1]
                    message = self._socket_manager.get_data_ready_to_transfer(self._socket_manager.offer)
                    self.server_socket.sendto(message, client_address)
                    self.ack()
                    break
                else:
                    print('(offer) Server still waiting for client request')
            except Exception as e:
                print('oops offer exception: ', e)
                print('Server No. ', self.server_id, ' Server waited too long for client. Try again Later...')
                break

    def ack(self):
        while True:
            try:
                print('(ack) Server No. ', self.server_id, ': Waiting for a client REQUEST')
                try:
                    time.sleep(self.server_id)
                    s_stream, client_address = self.server_socket.recvfrom(2048)  # any available port in the client
                except timeout:
                    print('Server No. ', self.server_id, ' Server waited too long for client. Try again Later...')
                    break
                d_message = self._socket_manager.decode_message(s_stream)
                self._socket_manager.set_original_string_start(d_message['original_string_start'])
                self._socket_manager.set_original_string_end(d_message['original_string_end'])
                print('(ack) Server No. ', self.server_id, ': Received a message from a client')
                if d_message['transfer_type'] == self._socket_manager.request:
                    s_start = d_message['original_string_start']
                    s_start = s_start.replace(" ", "")
                    print('Range start: ' + s_start)
                    print('Range start length is: ' + str(len(s_start)))
                    s_end = d_message['original_string_end']
                    s_end = s_end.replace(" ", "")
                    print('Range end: ' + s_end)
                    print('Range end length is: ' + str(len(s_end)))
                    print('(ack) Server No. ', self.server_id, ': Beginning Search')
                    result = self.find_string(s_start, s_end, self._socket_manager.hash_input)
                    if result is None:
                        print('(nack) Server No. ', self.server_id, 'Server NOT found hash')
                        message = self._socket_manager.get_data_ready_to_transfer(self._socket_manager.negative_acknowledge)
                        self.server_socket.sendto(message, client_address)
                    else:
                        time.sleep(3)
                        print('(ack) Server No. ', self.server_id, 'Server found hash')
                        self._socket_manager.set_original_string_start(result)
                        message = self._socket_manager.get_data_ready_to_transfer(self._socket_manager.acknowledge)
                        self.server_socket.sendto(message, client_address)
                    self.server_socket.close()
                    return True
                else:
                    print('Server still waiting for client request')
            except Exception as e:
                print('oops ack exception: ', e)
                print('Server No. ', self.server_id, ' Server waited too long for client. Try again Later...')
                return False

    def find_string(self, start_string, end_string, hash_input):
        print('hash input is: ' + hash_input)
        ranger = Cracker.Cracker(start_string, end_string)
        strings = list(ranger.generate_all_from_to_of_len())
        for string in strings:
            string_to_hash = hashlib.sha1(string.encode('utf-8')).hexdigest()
            if string_to_hash == hash_input:
                print('hash found!!! ' + string)
                return string
        return None

    def print_client_dict(self):
        for key, value in self.d_clients.items():
            print('-Server Map- Server No.: ', key, ', Client No.: ', value)

    def init_server_threads(self, count=2):
        for i in range(count):
            try:
                curr_thread = threading.Thread(target=self.threaded, args=(i+1,))
                self.list_threads.append(curr_thread)
            except Exception as e:
                print("Threads unexpected exception: ", e)
            finally:
                print('done initializing thread number: ', i+1)
        self.run_threads()
        self.terminate_threads()

    def threaded(self, thread_count):
        server = Server(self._socket_manager, thread_count)
        server.init_servers()

    def run_threads(self):
        for thread in self.list_threads:
            thread.start()

    def terminate_threads(self):
        for thread in self.list_threads:
            thread.join()


if __name__ == '__main__':

    server_count = 2
    socket_manager = SocketManager.SocketManager()
    server_manager = Server(socket_manager)
    server_manager.init_server_threads(server_count)
