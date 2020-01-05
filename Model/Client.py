import threading
from re import split
from socket import *
from struct import *
from Model import Config
from Model import Cracker


class Client:

    list_threads = []
    mutex_servers = threading.Lock()

    def __init__(self, server_hostname='255.255.255.255', server_port=3117):
        self.client_id = 1
        self.server_hostname = server_hostname
        self.server_port = server_port
        self.client_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)  # gets a random port
        # self.client_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # Enable broadcasting mode
        self.ip_broadcast = '255.255.255.255'
        self.l_servers = []
        self.config = Config.Config()
        self.config.set_team_name()
        self.config.set_hash_input('422ab519eac585ef4ab0769be5c019754f95e8dc')
        self.config.set_hash_length('6')
        self.cracker = Cracker.Cracker()
        print('Client: Initialized')

    def discover(self, count=1):
        for i in range(count):
            message = self.config.get_data_ready_to_transfer(self.config.discover)
            # discover_byte_stream = self.config.encode_message(self.config.discover)
            # self.client_socket.sendto(discover_byte_stream, (self.ip_broadcast, self.server_port))
            self.client_socket.sendto(message, (self.ip_broadcast, self.server_port))
            print('Client: Sent a DISCOVER')
            ans_byte_stream, server_address = self.client_socket.recvfrom(2048)  # callback function
            ans = self.config.decode_message(ans_byte_stream)
            d_message = self.config.get_decoded_message_to_dict(ans)
            # print('Client: Received OFFER from Server No. : ', ans)
            # self.l_servers.append((str(self.client_id), ans, str(i+1)))
            if d_message['transfer_type'] == self.config.offer:
                self.l_servers.append((str(self.client_id), str(i + 1)))
        self.print_list_of_tuples()

    def request(self):
        # real_ans = 'tashaf'
        # string_array = self.divide_two_domains(i_length, 2)
        # message = self.config.encode_message(s_input)
        # print('Client has sent a REQUEST with: ', s_input)
        self.config.set_original_string_start('aaa')
        self.config.set_original_string_end('zzz')
        message = self.config.get_data_ready_to_transfer(self.config.request)
        self.client_socket.sendto(message, (self.server_hostname, self.server_port))
        reply, server_address = self.client_socket.recvfrom(2048)
        ans = self.config.decode_message(reply)
        d_message = self.config.get_decoded_message_to_dict(ans)
        if d_message['transfer_type'] == self.config.acknowledge:
            print('Client has got the answer! ', ans)
        elif d_message['transfer_type'] == self.config.negative_acknowledge:
            print('Client has NOT got the answer! ', ans)
        self.client_socket.close()

    def print_list_of_tuples(self):
        # for loc1, loc2, loc3 in self.l_servers:
        #     print('-Client Map- Client No.: ' + loc1 + ', Server IP.: ' + loc2 + ', Server No.: ' + loc3)
        for loc1, loc2 in self.l_servers:
            print('-Client Map- Client No.: ' + loc2 + ', Server No.: ' + loc2)

    def init_threads(self, count=2):
        for i in range(count):
            try:
                curr_thread = threading.Thread(target=self.threaded, args=(i + 1))
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


# with threads #
# num_of_clients = 2
# client_manager = Client()
# client_manager.init_threads(num_of_clients)

# no threads #
print('Client initiated')
num_of_servers = 2
clnt = Client()
clnt.discover(num_of_servers)
clnt.request()

