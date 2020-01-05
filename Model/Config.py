from struct import *


class Config:

    d_bytes_structure = {}
    d_pre_encoded = {}

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

    def __init__(self):
        self.d_bytes_structure = {
                                'team_name': 32,
                                'transfer_type': 1,
                                'hash_input': 40,
                                'original_length': 1,
                                'original_string_start': 256,
                                'original_string_end': 256
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

    def set_team_name(self, s_team_name='cyber_cyber_cyber_cyber_cyber!'):
        self.team_name = s_team_name
        team_name_encoded = self.encode_message(s_team_name)
        self.d_pre_encoded.update({'team_name': team_name_encoded})

    def set_hash_input(self, s_hash_input):
        self.hash_input = s_hash_input
        hash_input_encoded = self.encode_message(s_hash_input)
        self.d_pre_encoded.update({'hash_input': hash_input_encoded})

    def set_hash_length(self, s_hash_length):
        self.original_length = s_hash_length
        hash_length_encoded = self.encode_message(s_hash_length)
        self.d_pre_encoded.update({'original_length': hash_length_encoded})

    def set_original_string_start(self, s_input):
        self.original_string_start = s_input
        s_input_encoded = self.encode_message(s_input)
        self.d_pre_encoded.update({'original_string_start': s_input_encoded})

    def set_original_string_end(self, s_input):
        self.original_string_end = s_input
        s_input_encoded = self.encode_message(s_input)
        self.d_pre_encoded.update({'original_string_end': s_input_encoded})

    def get_data_ready_to_transfer(self, transfer_type):
        return self.d_pre_encoded['team_name'] + self.d_pre_encoded[transfer_type] + self.d_pre_encoded['hash_input'] + self.d_pre_encoded['original_length'] + self.d_pre_encoded['original_string_start'] + self.d_pre_encoded['original_string_end']

    def encode_message(self, decoded_message):
        if not isinstance(decoded_message, str):
            decoded_message = str(decoded_message)
        message_utf8_format = decoded_message.encode('utf-8')
        s_bytes = bytes(message_utf8_format)
        message_tuple_byte_format = pack("I%ds" % (len(s_bytes),), len(s_bytes), s_bytes)
        return message_tuple_byte_format

    def encode_fixed_message(self, decoded_message, fixed_size_in_bits):
        if not isinstance(decoded_message, str):
            decoded_message = str(decoded_message)
        message_utf8_format = decoded_message.encode('utf-8')
        s_bytes = bytes(message_utf8_format)
        message_tuple_byte_format = pack("I", len(s_bytes)) + s_bytes
        return message_tuple_byte_format

    # def encode_message(self, decoded_message):
    #     message_utf8_format = decoded_message.encode('utf-8')
    #     s_bytes = bytes(message_utf8_format)
    #     message_tuple_byte_format = pack("I%ds" % (len(s_bytes),), len(s_bytes), s_bytes)
    #     return message_tuple_byte_format
    #
    # def decode_message(self, encoded_message):
    #     size = calcsize("I")
    #     message_byte_format = unpack("I", encoded_message[:size]), encoded_message[size:]
    #     decoded_message = message_byte_format[1]
    #     message = decoded_message.decode('utf-8')
    #     return message

    def decode_message(self, encoded_message):
        size = calcsize("I")
        message_byte_format = unpack("I", encoded_message[:size]), encoded_message[size:]
        decoded_message = message_byte_format[1]
        message = decoded_message.decode('utf-8')
        print(message)
        return message

    def get_decoded_message_to_dict(self, decoded_message):
        curr_d = {
                                'team_name': decoded_message[0:30],
                                'transfer_type': decoded_message[34:35],
                                'hash_input': decoded_message[39:79],
                                'original_length': decoded_message[83:84],
                                'original_string_start': decoded_message[88:344],
                                'original_string_end': decoded_message[348:604]
                                }
        return curr_d

    def print_dict(self, other_dict):
        for key, value in other_dict.items():
            print('Key: ', key, ', Value: ', value)

