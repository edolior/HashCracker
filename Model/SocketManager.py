from struct import *
from socket import *
from Model import Cracker
from Model.test import sha1
import hashlib
from Model import Task


class SocketManager:

    d_bytes_structure = {}
    d_pre_encoded = {}
    d_range = {}

    strings = []

    discover = '1'
    offer = '2'
    request = '3'
    acknowledge = '4'
    negative_acknowledge = '5'

    team_name = ''
    hash_input = ''
    original_length = ''
    original_string_start = ''
    original_string_end = ''
    server_address = ''

    server_count = 1

    cracker = None
    task = None

    def __init__(self):
        self.ip_broadcast = '255.255.255.255'
        self.ip_unicast = gethostname()
        self.server_hostname = gethostname()
        self.server_port = '3117'
        self.d_bytes_structure = {
                                'team_name': 32,
                                'transfer_type': 1,
                                'hash_input': 40,
                                'original_length': 1,
                                'original_string_start': 256,
                                'original_string_end': 256,
                                }
        self.d_pre_encoded.update({self.discover: self.encode_message(self.discover)})
        self.d_pre_encoded.update({self.offer: self.encode_message(self.offer)})
        self.d_pre_encoded.update({self.request: self.encode_message(self.request)})
        self.d_pre_encoded.update({self.acknowledge: self.encode_message(self.acknowledge)})
        self.d_pre_encoded.update({self.negative_acknowledge: self.encode_message(self.negative_acknowledge)})
        self.original_string_start = "a" * 256
        self.d_pre_encoded.update({'original_string_start': self.encode_message(self.original_string_start)})
        self.original_string_end = "z" * 256
        self.d_pre_encoded.update({'original_string_end': self.encode_message(self.original_string_end)})
        self.task = Task.Task()

    def set_configurations(self, team_name, hash_input, hash_length, server_count=2):
        self.set_team_name(team_name)
        self.set_hash_input(hash_input)
        self.set_hash_length(hash_length)
        self.server_count = server_count

    def set_team_name(self, s_team_name):
        self.team_name = s_team_name
        s_team_name = self.check_fill_stream(s_team_name, 'team_name')
        team_name_encoded = self.encode_message(s_team_name)
        self.d_pre_encoded.update({'team_name': team_name_encoded})

    def set_hash_input(self, s_hash_input):
        self.hash_input = s_hash_input
        s_hash_input = self.check_fill_stream(s_hash_input, 'hash_input')
        hash_input_encoded = self.encode_message(s_hash_input)
        self.d_pre_encoded.update({'hash_input': hash_input_encoded})

    def set_hash_length(self, s_hash_length):
        self.original_length = s_hash_length
        s_hash_length = self.check_fill_stream(s_hash_length, 'original_length')
        hash_length_encoded = self.encode_message(s_hash_length)
        self.d_pre_encoded.update({'original_length': hash_length_encoded})

    def set_original_string_start(self, s_input):
        self.original_string_start = s_input
        s_input = self.check_fill_stream(s_input, 'original_string_start')
        s_input_encoded = self.encode_message(s_input)
        self.d_pre_encoded.update({'original_string_start': s_input_encoded})

    def set_original_string_end(self, s_input):
        self.original_string_end = s_input
        s_input = self.check_fill_stream(s_input, 'original_string_end')
        s_input_encoded = self.encode_message(s_input)
        self.d_pre_encoded.update({'original_string_end': s_input_encoded})

    def get_data_ready_to_transfer(self, transfer_type):
        return self.d_pre_encoded['team_name'] + self.d_pre_encoded[transfer_type] + self.d_pre_encoded['hash_input'] + \
               self.d_pre_encoded['original_length'] + self.d_pre_encoded['original_string_start'] + self.d_pre_encoded[
                   'original_string_end']

    def encode_message(self, decoded_message):
        if not isinstance(decoded_message, str):
            decoded_message = str(decoded_message)
        message_utf8_format = decoded_message.encode('utf-8')
        s_bytes = bytes(message_utf8_format)
        message_tuple_byte_format = pack("I%ds" % (len(s_bytes),), len(s_bytes), s_bytes)
        return message_tuple_byte_format

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

    def decode_message(self, encoded_message):
        size = calcsize("I")
        message_byte_format = unpack("I", encoded_message[:size]), encoded_message[size:]
        decoded_message = message_byte_format[1]
        message = decoded_message.decode('utf-8')
        return message

    # def get_decoded_message_to_dict(self, decoded_message):
    #     d = {}
    #     const = 4
    #     agg_start = 0
    #     agg_end = 0
    #     for key, value in self.d_bytes_structure.items():
    #         agg_end += agg_start + self.d_bytes_structure[key]  # 32, 37, 81, 86
    #         d.update({key: decoded_message[agg_start:agg_end]})
    #         agg_start = agg_end + const  # 0, 36, 41, 85
    #     self.print_dict(d)
    #     return d

    def get_decoded_message_to_dict(self, decoded_message):
        d = {
                'team_name': decoded_message[0:32],
                'transfer_type': decoded_message[36:37],
                'hash_input': decoded_message[41:81],
                'original_length': decoded_message[85:86],
                'original_string_start': decoded_message[90:346],
                'original_string_end': decoded_message[350:606],
                }
        # self.print_dict(d)
        return d

    def init_task(self, offer_count):
        return self.task.divide_to_domains(int(self.original_length), offer_count)

    def print_dict(self, other_dict):
        for key, value in other_dict.items():
            print('Key: ', key, ', Value: ', value)

    def bind_server_address(self, tup_address):
        s_hostname = tup_address[0]
        s_port = str(tup_address[1])
        return s_hostname + ':' + s_port

    def unbind_server_address(self, s_address):
        return s_address.split(':')

    def print_list_of_tuples(self, l_tuple):
        # for loc1, loc2, loc3 in l_tuple:
        #     print('-Client Map- Client No.: ' + loc1 + ', Server IP.: ' + loc2 + ', Server No.: ' + loc3)
        for loc1, loc2 in l_tuple:
            print('-Client Map- Client No.: ' + loc2 + ', Server No.: ' + loc2)

    def print_list_of_strings(self, l_strings):
        for string in l_strings:
            print(string)
