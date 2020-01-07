class Cracker:

    def __init__(self,start_str, end_str):
        self._start_str = start_str
        self._end_str = end_str
        self._length = len(start_str)

    def _get_last_index_not_z(self, str_list):
        for i, char in enumerate(str_list[::-1]):
            if char is not 'z':
                return self._length - 1 - i

    def _make_all_chars_after_index_into_a(self, str_list, index):
        for i in range(index + 1, self._length):
            str_list[i] = 'a'

    def generate_all_from_to_of_len(self):
        tmp = list(self._start_str)
        last = list(self._end_str)
        yield "".join(tmp)
        while tmp != last:
            i = self._get_last_index_not_z(tmp)
            tmp[i] = chr(ord(tmp[i]) + 1)
            if i is not len(tmp) - 1:
                self._make_all_chars_after_index_into_a(tmp, i)
            yield "".join(tmp)
        yield "".join(last)


# if __name__ == '__main__':
#     test = Cracker('fff', 'zdv')
#     for string in test.generate_all_from_to_of_len():
#         print(string)
