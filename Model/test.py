import concurrent.futures
import hashlib
from builtins import print
import time
from Model import Cracker


def sha1(str):
    #encoding str using encode()
    #then sending to SHA1()
    # result = hashlib.sha1(str.encode('utf-8')).digest()
    result = hashlib.sha1(str.encode('utf-8')).hexdigest()
    # print the equivalent hexadecimal value
    # print(result.hexdigest())
    # return result.decode('utf-8')
    return result


def find_string(start_string, end_string, hash_input):
    ranger = Cracker(start_string, end_string)
    strings = list(ranger.generate_all_from_to_of_len())
    for string in strings:
        if sha1(string) == hash_input:
            # print("The string is: " + string)
            return string
    return None


if __name__ == '__main__':

    teamName = "IYteam"
    print("Welcome to < " + teamName + " >. Please enter a hash:")
    x = input()
    # x = sha1("mmm")
    print(x)
    # print(sha1("hello"))
    print("Please enter the input string length:")
    lenOfString = int(input())
    # lenOfString = 3
    start_time = time.time()
    cracker = Cracker.Cracker('a'*lenOfString, 'z'*lenOfString)
    strings = list(cracker.generate_all_from_to_of_len())
    num_of_servers = 16
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_servers) as executor:
        futures = list()
        for i in range(num_of_servers):
            start_index = int(i*(len(strings)/num_of_servers))
            end_index = int((i+1)*(len(strings)/num_of_servers)) - 1
            future = executor.submit(find_string, strings[start_index], strings[end_index], x)
            futures.append(future)
            return_value = future.result()
            print(return_value)
    end_time = time.time()
    print(f"Time: {end_time-start_time}")
