

class View:

    def __init__(self, controller):
        self._controller = controller

    def run_view(self):

        team_name = self.user_input_team_name()
        hash_input = self.user_input_hash(team_name)
        hash_length = self.user_input_hash_length()

        print('Amount of servers?')
        server_count = input()

        print('Amount of clients?')
        client_count = input()

        print('Begin? y/n')
        begin_value = input()
        if begin_value == 'y':
            # self._controller.run_threaded_app(team_name, hash_input, hash_length, server_count)
            # self._controller.run_app(team_name, hash_input, hash_length, server_count)
            self._controller.run_server(team_name, hash_input, hash_length, server_count=2)
            self._controller.run_client(team_name, hash_input, hash_length, client_count=1)
        else:
            print('Goodbye it was fantastic!')

    def user_input_team_name(self):
        print('Type your team name (32 characters)')
        team_name = input()
        team_name = self._controller.check_fill_stream(team_name)
        return team_name

    def user_input_hash(self, team_name):
        print('Welcome to ' + team_name + '. Please enter the hash:')
        flag_hash_input = False
        while not flag_hash_input:
            hash_input = input()
            try:
                int(hash_input, 16)
                flag_hash_input = True
            except ValueError:
                print('Your hash input is not hexadecimal please try again.')
                flag_hash_input = False
        return hash_input

    def user_input_hash_length(self):
        print('Please enter the input string length:')
        flag_hash_length_input = False
        while not flag_hash_length_input:
            hash_length = input()
            if int(hash_length) <= 0:
                flag_hash_length_input = True
            else:
                print('Your hash length input must be larger than zero.')
                flag_hash_length_input = False
        return hash_length
