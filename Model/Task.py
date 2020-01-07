import hashlib
import time

ALPHABET_SIZE = 26


class Task:

    def divide_to_domains(self, original_len, num_of_servers):
        """
        divide tasks to n servers fairly
        :raise TypeError if len or servers are not integers
        :param original_len: length of strings in search ranges
        :param num_of_servers: amount of servers requiring for task
        :return: return list of tasks: [(start1,end1), (start2,end2),...,(startn,endn)]
           where n is the amount of servers available to work
        """
        if int(original_len) != original_len:
            raise TypeError("length of string must be integer")
        if int(num_of_servers) != num_of_servers:
            raise TypeError("amount of server must be integer")

        domains = [None] * num_of_servers
        last = 'z' * original_len

        count_permutations = self.__get_count_permutations(original_len)
        per_server = count_permutations // num_of_servers
        str_as_int = 0
        for i in range(len(domains)):
            start = self.__get_string_value(str_as_int, original_len)
            if str_as_int >= count_permutations:
                start = last
            str_as_int += per_server
            end = self.__get_string_value(str_as_int, original_len)
            if str_as_int >= count_permutations:
                end = last
            domains[i] = (start, end)
            str_as_int += 1
        domains[len(domains) - 1] = (domains[len(domains) - 1][0], last)
        return domains

    def __get_count_permutations(self, strLen):
        """
        :param strLen: length of required strings
        :return: amount of different strings could be generated in given length
        """
        return ALPHABET_SIZE ** strLen

    def __get_string_value(self, to_convert, length):
        """
        translate int to string with given len
         when 0 is 'aaa...a'
        :param to_convert: integer value of string
        :param length: required string length
        :return: string value of given number with given length
        """
        str_val = ""
        while to_convert > 0:
            c = int(to_convert % 26)
            str_val = chr(c + 97) + str_val
            to_convert = int(to_convert // 26)
            length = length - 1
        while length > 0:
            str_val = 'a' + str_val
            length -= 1
        return str_val

# if __name__ == '__main__':
#     t = time.time()
#     task = Task()
#     ans = task.divide_to_domains(53, 20)
#     t = time.time() - t
#     print(t)
