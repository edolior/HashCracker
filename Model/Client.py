import threading
from re import split
from socket import *
from struct import *
from Model import SocketManager
from Model import Cracker
import time
from Model import Task
# import socket.timeout as TimeoutException


class Client:

    list_threads = []
    mutex_servers = threading.Lock()
    d_servers = {}
    client_socket = None
    offer_count = 0

    def __init__(self, ref_socket_manager, client_id=1):
        self._socket_manager = ref_socket_manager
        self.client_id = client_id
        self.d_servers[self.client_id] = []
        self.init_client_socket()
        self.task = Task.Task()
        # self.cracker = Cracker.Cracker()

    def init_client_socket(self):
        self.client_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)  # gets a random port
        self.client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # Enable broadcasting mode

        self.client_socket.settimeout(20)

        # self.curr_server_address = self._socket_manager.server_hostname + ':' + self._socket_manager.server_port
        # self.client_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)

    def discover(self):
        message = self._socket_manager.get_data_ready_to_transfer(self._socket_manager.discover)
        self.client_socket.sendto(message, (self._socket_manager.ip_broadcast, int(self._socket_manager.server_port)))
        print('Client: Sent a DISCOVER')
        while self.offer_count < self._socket_manager.server_count:
            self.mutex_servers.acquire()
            try:
                ans_byte_stream, server_address = self.client_socket.recvfrom(2048)  # callback function
            except timeout:
                self.offer_count += 1
                print("Client waited too long for server. Try again Later...")
                continue
            self.mutex_servers.release()
            ans = self._socket_manager.decode_message(ans_byte_stream)
            d_message = self._socket_manager.get_decoded_message_to_dict(ans)
            self._socket_manager.print_dict(d_message)
            if d_message['transfer_type'] == self._socket_manager.offer:
                self.offer_count += 1
                s_server_address = self._socket_manager.bind_server_address(server_address)
                print('address: ' + s_server_address)
                print('Client: Received OFFER from Server No. : ', server_address)
                self.d_servers[self.client_id].append(s_server_address)
        self._socket_manager.print_dict(self.d_servers)
        self.request()

    def request(self):
        for i in range(self.offer_count):
            string_list = self._socket_manager.init_task(self._socket_manager.server_count)
            print('client: hash input is: ' + self._socket_manager.hash_input)
            self._socket_manager.print_list_of_strings(string_list)
            s_range_start = string_list[i][0]
            s_range_end = string_list[i][1]
            self._socket_manager.set_original_string_start(s_range_start)
            self._socket_manager.set_original_string_end(s_range_end)
            curr_server_address = self.d_servers[self.client_id][i]
            s_hostname = self._socket_manager.unbind_server_address(curr_server_address)[0]
            s_port = self._socket_manager.unbind_server_address(curr_server_address)[1]
            message = self._socket_manager.get_data_ready_to_transfer(self._socket_manager.request)
            self.client_socket.sendto(message, (s_hostname, int(s_port)))
            print('Client has sent a REQUEST No. ' + str(i+1) + ' to server: ' + curr_server_address)
            time.sleep(3)
        try:
            reply, server_address = self.client_socket.recvfrom(2048)  # callback function
        except timeout:
            print("Client waited too long for server. Try again Later...")
        ans = self._socket_manager.decode_message(reply)
        d_message = self._socket_manager.get_decoded_message_to_dict(ans)
        if d_message['transfer_type'] == self._socket_manager.acknowledge:
            hash_ans = d_message['original_string_start']
            print('Client has got the answer! ', hash_ans, 'from server: ' + curr_server_address)
        elif d_message['transfer_type'] == self._socket_manager.negative_acknowledge:
            print('Client has NOT got the answer from server: ' + curr_server_address)
        self.client_socket.close()

    def init_threads(self, count=2):
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
                print('done initializing thread number: ', i + 1)
        self.run_threads()
        self.terminate_threads()

    def threaded(self, thread_count):
        num_of_servers = 2
        client = Client(thread_count)
        client.discover(num_of_servers)
        client.request()

    def run_threads(self):
        for thread in self.list_threads:
            thread.start()

    def terminate_threads(self):
        for thread in self.list_threads:
            thread.join()


if __name__ == '__main__':
    team_name = 'cyber_cyber_cyber_cyber_cyber!!!'
    # hash_input = '422ab519eac585ef4ab0769be5c019754f95e8dc'
    # hash_length = '6'
    # hash_input = 'e0c9035898dd52fc65c41454cec9c4d2611bfb37'
    # hash_length = '2'
    # hash_input = 'a9993e364706816aba3e25717850c26c9cd0d89d'
    # hash_length = '3'
    hash_input = 'b60d121b438a380c343d5ec3c2037564b82ffef3'
    hash_length = '3'
    client_count = 1
    server_count = 2
    socket_manager = SocketManager.SocketManager()
    socket_manager.set_configurations(team_name, hash_input, hash_length, server_count)
    client = Client(socket_manager, client_count)
    client.discover()

