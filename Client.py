from socket import *
import threading
import SocketManager
import time
import Ranger


class Client:

    list_threads = []
    mutex_servers = threading.Lock()
    d_servers = {}
    client_socket = None
    offer_count = 0

    def __init__(self, ref_socket_manager, client_id=0):
        self._socket_manager = ref_socket_manager
        self.client_id = client_id
        self.d_servers[self.client_id] = []
        self.init_client_socket()
        self.task = Ranger.Ranger()

    def init_client_socket(self):
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # Enable broadcasting mode
        self.client_socket.settimeout(15)
        # self.client_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)  # Enables UDP
        # self.client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # Enables multiple clients in same address
        print('Client No. ', self.client_id, ': Socket is listening')

    def discover(self):
        b_timeout = False
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
                b_timeout = True
                break
            self.mutex_servers.release()
            d_message = self._socket_manager.decode_message(ans_byte_stream)
            self._socket_manager.print_dict(d_message)
            if d_message['transfer_type'] == self._socket_manager.offer:
                self.offer_count += 1
                s_server_address = self._socket_manager.bind_server_address(server_address)
                print('Client: Received OFFER from Server No. : ', server_address)
                self.d_servers[self.client_id].append(s_server_address)
        if not b_timeout:
            self.request()

    def request(self):
        try:
            for i in range(self.offer_count):
                string_list = self._socket_manager.init_task(self._socket_manager.server_count)
                print('client: hash input is: ' + self._socket_manager.hash_input)
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
                time.sleep(2)
            while True:
                try:
                    reply, server_address = self.client_socket.recvfrom(2048)  # callback function
                except timeout:
                    print("Client waited too long for server. Try again Later...")
                    break
                d_message = self._socket_manager.decode_message(reply)
                if d_message['transfer_type'] == self._socket_manager.acknowledge:
                    hash_ans = d_message['original_string_start']
                    hash_ans = hash_ans.replace(" ", "")
                    print('Client has got the answer! ', hash_ans, 'from server: ' + curr_server_address)
                elif d_message['transfer_type'] == self._socket_manager.negative_acknowledge:
                    print('Client has NOT got the answer from server: ' + curr_server_address)
        except Exception as e:
            print("Client waited too long for server. Try again Later...")
            self.client_socket.close()
        self.client_socket.close()

    def init_threads(self, count=2):
        for i in range(count):
            try:
                curr_thread = threading.Thread(target=self.threaded, args=(i+1,))
                self.list_threads.append(curr_thread)
            except Exception as e:
                print("Threads unexpected exception: ", e)
            finally:
                print('done initializing thread number: ', i + 1)
        self.run_threads()
        self.terminate_threads()

    def threaded(self, thread_count):
        this_client = Client(self._socket_manager, thread_count)
        this_client.discover()

    def run_threads(self):
        for thread in self.list_threads:
            thread.start()

    def terminate_threads(self):
        for thread in self.list_threads:
            thread.join()


if __name__ == '__main__':

    # Uncomment to use an example! #
    # team_name = 'CyberX5'
    # hash_input = 'b60d121b438a380c343d5ec3c2037564b82ffef3'
    # hash_length = 3

    socket_manager = SocketManager.SocketManager()
    team_name = socket_manager.user_input_team_name()
    hash_input = socket_manager.user_input_hash(team_name)
    hash_length = socket_manager.user_input_hash_length()
    socket_manager.set_configurations(team_name, hash_input, int(hash_length))

    # 1 Client #
    client = Client(socket_manager)
    client.discover()

    # Multiple Clients #
    # client_count = 2
    # client_manager = Client(socket_manager)
    # client_manager.init_threads(client_count)

