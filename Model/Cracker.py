

class Cracker:

    def divide_two_domains(self, i_length, num_of_servers=2):
        domains = [None] * num_of_servers * 2
        first = ""
        last = ""
        i = 0
        while i < i_length:
            first = first + 'a'  # aaa
            last = last + 'z'  # zzz
            i = i + 1
        total = self.convert_string_to_int(last)
        per_server = total / num_of_servers
        domains[0] = first
        domains[domains.__len__() - 1] = last
        sum = 0
        j = 1
        while j <= domains.__len__() - 2:
            sum = sum + per_server
            domains[j] = self.convert_int_to_string(sum, len)  # end domain of server
            sum = sum + 1
            domains[j + 1] = self.convert_int_to_string(sum, len)  # start domain of next server
            j = j + 2
        return domains


    def convert_string_to_int(self, s_word):
        char_array = split(s_word)
        num = 0
        for c in char_array:
            if c < 'a' or c > 'z':
                raise RuntimeError("invalid")
            num = num * 26
            num = num + ord(c) - 97
        return num


    def convert_int_to_string(self, to_convert, length):
        s = ""
        while to_convert > 0:
            c = int(to_convert % 26)
            s = chr(c + 97) + s
            to_convert = int(to_convert / 26)
            length = length - 1
        while length > 0:
            s = 'a' + s
            length = length - 1
        return s


    def split(self, word):
        return [char for char in word]