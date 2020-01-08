import logging
import hashlib
import threading
from re import split
from socket import *
from struct import *
from Model import SocketManager
from Model import Task
from Model import Cracker
import time


class Server:

    mutex_clients = threading.Lock()
    d_clients = {}
    list_threads = []
    server_socket = None
    curr_server_address = ''

    def __init__(self, socket_manager, server_id=0):
        self._socket_manager = socket_manager
        self.server_id = server_id
        self.task = Task.Task()

    def init_servers(self):
        self.init_sockets()
        self.offer()

    def init_sockets(self):
        # self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # print(self._socket_manager.server_hostname)
        self.server_socket.bind(('0.0.0.0', int(self._socket_manager.server_port)))
        #self.server_socket.bind((self._socket_manager.server_hostname, int(self._socket_manager.server_port)))
        # self.server_socket.bind(('', int(self._socket_manager.server_port)))
        self.curr_server_address = self._socket_manager.server_hostname + ':' + self._socket_manager.server_port

        self.server_socket.settimeout(30)  # Set a timeout so the socket does not block when trying to receive data.

        # self._socket_manager.set_curr_server_address(self.curr_server_address)
        # self.server_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        # self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        # self.server_socket.listen(5)  # queue up to 5 connection requests before refusing outside connections
        # self.server_socket.listen(1)
        print('Server No. ', self.server_id, ': Socket is listening')

    def offer(self):
        while True:
            try:
                # self.mutex_clients.acquire()  # lock acquired to avoid client collision
                print('(offer) Server No. ', self.server_id, ': Waiting for a client DISCOVER')
                try:
                    s_stream, client_address = self.server_socket.recvfrom(2048)  # callback function
                except timeout:
                    print('(offer) Server No. ', self.server_id, ' Server waited too long for client. Try again Later...')
                    # self.mutex_clients.release()
                    break
                # self.mutex_clients.release()
                d_message = self._socket_manager.decode_message(s_stream)
                self._socket_manager.set_team_name(d_message['team_name'])
                self._socket_manager.set_hash_input(d_message['hash_input'])
                self._socket_manager.set_hash_length(d_message['original_length'])
                self._socket_manager.set_original_string_start(d_message['original_string_start'])
                self._socket_manager.set_original_string_end(d_message['original_string_end'])

                # d_message = self._socket_manager.get_decoded_message_to_dict(message)
                # self._socket_manager.print_dict(d_message)

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
                print('Server nack')
                break

    def ack(self):
        while True:
            try:
                print('(ack) Server No. ', self.server_id, ': Waiting for a client REQUEST')
                try:
                    time.sleep(self.server_id)
                    # self.mutex_clients.acquire()
                    s_stream, client_address = self.server_socket.recvfrom(2048)  # any available port in the client
                    # self.mutex_clients.release()
                except timeout:
                    print('(ack) Server No. ', self.server_id, ' Server waited too long for client. Try again Later...')
                    print('Server nack')
                    # self.mutex_clients.release()
                    break
                # self.mutex_clients.release()
                d_message = self._socket_manager.decode_message(s_stream)
                # d_message = self._socket_manager.get_decoded_message_to_dict(message)
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
                        # real_ans = 'tashaf'
                        message = self._socket_manager.get_data_ready_to_transfer(self._socket_manager.acknowledge)
                        self.server_socket.sendto(message, client_address)
                    self.server_socket.close()
                    # client_address.close()
                    return True
                else:
                    print('Server still waiting for client request')
            except Exception as e:
                print('oops ack exception: ', e)
                # self.mutex_clients.release()
                # self.server_socket.close()
                # client_address.close()
                return False

    def find_string(self, start_string, end_string, hash_input):
        print('hash input is: ' + hash_input)
        ranger = Cracker.Cracker(start_string, end_string)
        strings = list(ranger.generate_all_from_to_of_len())
        for string in strings:
            # string = string.encode('utf-8')
            string_to_hash = self.sha1(string)
            # print('string to hash is: ' + string_to_hash)
            if string_to_hash == hash_input:
                print('hash found!!! ' + string)
                return string
            # if hashlib.sha1(string) == hash_input:
            #     print('hash found!!! ' + string)
            #     return string
        return None

    def sha1(self, string_to_check):
        # encoding str using encode()
        # then sending to SHA1()
        # result = hashlib.sha1(str.encode('utf-8')).digest()
        result = hashlib.sha1(string_to_check.encode('utf-8')).hexdigest()
        # print the equivalent hexadecimal value
        # print(result.hexdigest())
        # return result.decode('utf-8')
        return result

    def tuple_to_string(self, tup):
        s_host = ''.join(tup[0])
        s_port = ''.join(str(tup[1]))
        return s_host + ':' + s_port

    def print_dict(self):
        for key, value in self.d_clients.items():
            print('-Server Map- Server No.: ', key, ', Client No.: ', value)

    def init_server_threads(self, count=2):
        for i in range(count):
            try:
                curr_thread = threading.Thread(target=self.threaded, args=(i+1,))
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

    socket_manager = SocketManager.SocketManager()

    # team_name = socket_manager.user_input_team_name()
    # hash_input = socket_manager.user_input_hash(team_name)
    # hash_length = socket_manager.user_input_hash_length()
    #
    # print('Amount of servers?')
    # server_count = input()
    #
    # print('Amount of clients?')
    # client_count = input()

    # team_name = 'cyber_cyber_cyber_cyber_cyber!!!'
    # hash_input = '422ab519eac585ef4ab0769be5c019754f95e8dc'
    # hash_length = '6'
    # hash_input = 'e0c9035898dd52fc65c41454cec9c4d2611bfb37'
    # hash_length = '2'
    # hash_input = 'a9993e364706816aba3e25717850c26c9cd0d89d'
    # hash_length = '3'

    # hash_input = 'b60d121b438a380c343d5ec3c2037564b82ffef3'
    # hash_length = 3
    # hash_input = ''
    # hash_length = 0

    server_count = 2

    # socket_manager.set_configurations(team_name, hash_input, hash_length, server_count)
    server_manager = Server(socket_manager)
    server_manager.init_server_threads(server_count)
