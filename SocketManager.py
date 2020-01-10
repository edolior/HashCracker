from struct import *
from socket import *
import Ranger


class SocketManager:

    d_bytes_structure = {}
    d_bytes_format = {}
    d_pre_encoded = {}
    d_range = {}

    strings = []

    discover = 1
    offer = 2
    request = 3
    acknowledge = 4
    negative_acknowledge = 5

    team_name = ''
    hash_input = ''
    original_length = 0
    original_string_start = ''
    original_string_end = ''
    server_address = ''

    server_count = 0

    cracker = None
    task = None

    def __init__(self):
        self.ip_broadcast = '255.255.255.255'
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
        self.d_bytes_format = {
                                'team_name': '32s',
                                'transfer_type': 'b',
                                'hash_input': '40s',
                                'original_length': 'b',
                                'original_string_start': '256s',
                                'original_string_end': '256s',
                                }
        self.d_pre_encoded.update({self.discover: pack('b', self.discover)})
        self.d_pre_encoded.update({self.offer: pack('b', self.offer)})
        self.d_pre_encoded.update({self.request: pack('b', self.request)})
        self.d_pre_encoded.update({self.acknowledge: pack('b', self.acknowledge)})
        self.d_pre_encoded.update({self.negative_acknowledge: pack('b', self.negative_acknowledge)})
        self.original_string_start = "a" * 256
        self.original_string_start = self.original_string_start.encode('utf-8')
        self.d_pre_encoded.update({'original_string_start': pack('256s', self.original_string_start)})
        self.original_string_end = "z" * 256
        self.original_string_end = self.original_string_end.encode('utf-8')
        self.d_pre_encoded.update({'original_string_end': pack('256s', self.original_string_end)})
        self.task = Ranger.Ranger()

    def set_configurations(self, team_name, hash_input, hash_length, server_count=2):
        self.set_team_name(team_name)
        self.set_hash_input(hash_input)
        self.set_hash_length(hash_length)
        self.server_count = server_count

    def set_team_name(self, s_team_name):
        self.team_name = s_team_name
        s_team_name = self.check_fill_stream(s_team_name, 'team_name')
        s_team_name = s_team_name.encode('utf-8')
        team_name_encoded = pack('32s', s_team_name)
        self.d_pre_encoded.update({'team_name': team_name_encoded})

    def set_hash_input(self, s_hash_input):
        self.hash_input = s_hash_input
        s_hash_input = s_hash_input.encode('utf-8')
        if s_hash_input == '':
            s_hash_input = self.check_fill_stream(s_hash_input, 'hash_input')
        hash_input_encoded = pack('40s', s_hash_input)
        self.d_pre_encoded.update({'hash_input': hash_input_encoded})

    def set_hash_length(self, hash_length):
        if hash_length == 0:
            hash_length = 1
        self.original_length = hash_length
        hash_length_encoded = pack('b', hash_length)
        self.d_pre_encoded.update({'original_length': hash_length_encoded})

    def set_original_string_start(self, s_input):
        self.original_string_start = s_input
        s_input = self.check_fill_stream(s_input, 'original_string_start')
        s_input = s_input.encode('utf-8')
        s_input_encoded = pack('256s', s_input)
        self.d_pre_encoded.update({'original_string_start': s_input_encoded})

    def set_original_string_end(self, s_input):
        self.original_string_end = s_input
        s_input = self.check_fill_stream(s_input, 'original_string_end')
        s_input = s_input.encode('utf-8')
        s_input_encoded = pack('256s', s_input)
        self.d_pre_encoded.update({'original_string_end': s_input_encoded})

    def get_data_ready_to_transfer(self, transfer_type):
        return self.d_pre_encoded['team_name'] + self.d_pre_encoded[transfer_type] + self.d_pre_encoded['hash_input'] + \
               self.d_pre_encoded['original_length'] + self.d_pre_encoded['original_string_start'] + self.d_pre_encoded[
                   'original_string_end']

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

        team_name_bytes = self.d_bytes_format['team_name']
        transfer_type_bytes = self.d_bytes_format['transfer_type']
        hash_input = self.d_bytes_format['hash_input']
        original_length = self.d_bytes_format['original_length']
        original_string_start = self.d_bytes_format['original_string_start']
        original_string_end = self.d_bytes_format['original_string_end']

        s_unpack = team_name_bytes + transfer_type_bytes + hash_input + original_length + original_string_start + original_string_end
        team_name, transfer_type, hash_input, original_length, original_string_start, original_string_end = unpack(s_unpack, encoded_message)
        team_name = unpack('32s', team_name)
        team_name = team_name[0].decode('utf-8')
        hash_input = unpack('40s', hash_input)
        hash_input = hash_input[0].decode('utf-8')
        original_string_start = unpack('256s', original_string_start)
        original_string_start = original_string_start[0].decode('utf-8')
        original_string_end = unpack('256s', original_string_end)
        original_string_end = original_string_end[0].decode('utf-8')

        self.set_team_name(team_name)
        self.set_hash_input(hash_input)
        self.set_hash_length(original_length)
        self.set_original_string_start(original_string_start)
        self.set_original_string_end(original_string_end)

        d = {}
        d.update({'team_name': team_name})
        d.update({'transfer_type': transfer_type})
        d.update({'hash_input': hash_input})
        d.update({'original_length': original_length})
        d.update({'original_string_start': original_string_start})
        d.update({'original_string_end': original_string_end})
        return d

    @staticmethod
    def decode_format(encoded_message, s_format):
        if s_format == 'string':
            size = calcsize("I")
            message_byte_format = unpack("I", encoded_message[:size]), encoded_message[size:]
            decoded_message = message_byte_format[1]
            message = decoded_message.decode('utf-8')
            return message
        elif s_format == 'int':
            message = unpack("b", encoded_message)
            return message[0]
        elif s_format == 'unknown' and encoded_message:
            print('Detected Leakage but will make corrections.')

    @staticmethod
    def tuple_to_string(tup):
        s_host = ''.join(tup[0])
        s_port = ''.join(str(tup[1]))
        return s_host + ':' + s_port

    def get_decoded_by_loop(self, decoded_message):
        d = {}
        const = 4
        agg_start = 0
        agg_end = 0
        for key, value in self.d_bytes_structure.items():
            agg_end += agg_start + self.d_bytes_structure[key]  # 32, 37, 81, 86
            d.update({key: decoded_message[agg_start:agg_end]})
            agg_start = agg_end + const  # 0, 36, 41, 85
        self.print_dict(d)
        return d

    @staticmethod
    def get_decoded_by_range(decoded_message):
        return {
                'team_name': decoded_message[0:32],
                'transfer_type': decoded_message[36:37],
                'hash_input': decoded_message[41:81],
                'original_length': decoded_message[85:86],
                'original_string_start': decoded_message[90:346],
                'original_string_end': decoded_message[350:606],
                'extra': decoded_message[610:614]
                }

    def init_task(self, offer_count):
        return self.task.divide_to_domains(int(self.original_length), offer_count)

    @staticmethod
    def print_dict(other_dict):
        for key, value in other_dict.items():
            print('Key: ', key, ', Value: ', value)

    @staticmethod
    def bind_server_address(tup_address):
        s_hostname = tup_address[0]
        s_port = str(tup_address[1])
        return s_hostname + ':' + s_port

    @staticmethod
    def unbind_server_address(s_address):
        return s_address.split(':')

    @staticmethod
    def print_list_of_tuples(l_tuple):
        for loc1, loc2 in l_tuple:
            print('-Client Map- Client No.: ' + loc2 + ', Server No.: ' + loc2)

    @staticmethod
    def print_list_of_strings(l_strings):
        for string in l_strings:
            print(string)

    def user_input_team_name(self):
        print('Type your team name (32 characters)' + '\n')
        team_name = input()
        team_name = self.check_fill_stream(team_name, 'team_name')
        return team_name

    @staticmethod
    def user_input_hash(team_name):
        print('Welcome team ' + team_name + '\n' + 'Please enter the hash:' + '\n')
        hash_input = input()
        try:
            int(hash_input, 16)
        except ValueError:
            print('Your hash input is not hexadecimal please try again.' + '\n')
        return hash_input

    @staticmethod
    def user_input_hash_length():
        print('Please enter the input string length:' + '\n')
        flag_hash_length_input = False
        while not flag_hash_length_input:
            hash_length = input()
            if int(hash_length) > 0:
                flag_hash_length_input = True
            else:
                print('Your hash length input must be larger than zero.')
                flag_hash_length_input = False
        return hash_length
