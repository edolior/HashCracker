

class View:

    def __init__(self, controller):
        self._controller = controller

    def run_view(self):
        # print('Type your team name (32 characters)')
        # team_name = input()
        # if len(team_name) < self._controller.team_name_length:
        #     team_name = "{:<15}".format(team_name)
        # elif len(team_name) > self._controller.team_name_length:
        #     team_name = team_name[0:33]
        # print('Welcome to ' + team_name + '. Please enter the hash:')
        # hash_input = input()
        # print('Please enter the input string length:')
        # hash_length = input()
        # print('Amount of servers?')
        # server_count = input()
        # print('Begin? y/n')
        # begin_value = input()
        # if begin_value == 'y':
        #     # self._controller.run_threaded_app(team_name, hash_input, hash_length, server_count)
        #     self._controller.run_app(team_name, hash_input, hash_length, server_count)
        # else:
        #     print('Goodbye it was fantastic!')

        # server_count = 2
        # self._controller.run_server(team_name, hash_input, hash_length, server_count)

        client_count = 1
        # self._controller.run_client(team_name, hash_input, hash_length, client_count)
