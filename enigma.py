import copy
import json
import sys

# Encryption parameters
W1_IDX = 0
W2_IDX = 1
W3_IDX = 2
W1_MULT = 2
DEFINED_MOD = 26
ENCRYPTED = 1
NOT_ENCRYPTED = 0

# Run command parameters
FLAG_STEP_SIZE = 2
FLAG_STARTING_IDX = 1
POSSIBLE_ARGS_AMOUNT = (5, 7)


class JSONFileError(Exception):
    def __init__(self, message = "JSON file is not valid"):
        self.message = message
        Exception.__init__(self, message)


def load_enigma_from_path(path):
    try:
        with open(path, 'r') as file:
            maps = json.load(file)
    except Exception:
        raise JSONFileError()

    hash_map = maps['hash_map']
    wheels = maps['wheels']
    reflector_map = maps['reflector_map']
    return Enigma(hash_map, wheels, reflector_map)


class Enigma:
    def __init__(self, hash_map, wheels, reflector_map):
        self.hash_map = hash_map
        self.wheels = wheels
        self.reflector_map = reflector_map

    def encrypt(self, message):
        tmp_wheels = copy.deepcopy(self.wheels)
        encrypted_list = []
        count = 0
        for char in message:
            encrypted_char, add_to_count = self.encrypt_char(char, tmp_wheels)
            encrypted_list.append(encrypted_char)
            count += add_to_count
            rotate_wheels(count, tmp_wheels)
        return ''.join(encrypted_list)

    def encrypt_char(self, char, tmp_wheels):
        # Check if encryption is not needed
        if char.islower() is False:
            result = (char, NOT_ENCRYPTED)
            return result

        # Encryption is needed. start the process
        i = self.hash_map[char]
        mod_result = (((tmp_wheels[W1_IDX] * W1_MULT) - tmp_wheels[W2_IDX] +
                       tmp_wheels[W3_IDX]) % DEFINED_MOD)
        if mod_result == 0:
            i += 1
        else:
            i += mod_result
        i = i % DEFINED_MOD

        # match char to c1 from hash that matches i
        c1 = ''
        for key in self.hash_map.keys():
            if self.hash_map[key] == i:
                c1 = key
                break

        # match char to c2 from refl that matches c1
        c2 = self.reflector_map[c1]

        i = self.hash_map[c2]
        if mod_result == 0:
            i -= 1
        else:
            i -= mod_result
        i = i % DEFINED_MOD

        c3 = ''
        for key in self.hash_map.keys():
            if self.hash_map[key] == i:
                c3 = key
                break

        # Encryption finished
        result = (c3, ENCRYPTED)
        return result


def rotate_wheels(count, tmp_wheels):
    tmp_wheels[W1_IDX] = 1 if tmp_wheels[W1_IDX] == 8\
        else tmp_wheels[W1_IDX] + 1
    tmp_wheels[W2_IDX] = tmp_wheels[W2_IDX] * 2 if count % 2 == 0\
        else tmp_wheels[W2_IDX] - 1
    if count % 10 == 0:
        tmp_wheels[W3_IDX] = 10
    elif count % 3 == 0:
        tmp_wheels[W3_IDX] = 5
    else:
        tmp_wheels[W3_IDX] = 0


def bad_params_err():
    sys.stderr.write("Usage: python3 enigma.py -c <config_file> -i <input_file>"
                     " -o <output_file>\n")
    exit(1)


def runtime_script_err():
    sys.stderr.write("The enigma script has encountered an error\n")
    exit(1)


def input_validation(input_list):
    """
    Validates the Run command given when module is activated through script, due
    to the following conditions:
    1. Legitimacy of arguments amount in the command.
    2. Run command holds necessary flags.
    :param input_list: run command values set in order in a list
    :return args_dict: dictionary holding matching flags and arguments
    """

    # Validates that the amount of arguments received is legal
    if len(input_list) not in POSSIBLE_ARGS_AMOUNT:
        bad_params_err()

    # Matches flag to path. Checks whether paths are missing and validates flags
    necessary_flags = ['-c', '-i']
    valid_flags = necessary_flags + ['-o']
    args_dict = { }

    for i in range(FLAG_STARTING_IDX, len(input_list), FLAG_STEP_SIZE):
        try:
            if input_list[i] in valid_flags:
                args_dict[input_list[i]] = input_list[i + 1]
            else:
                bad_params_err()
        except Exception:
            bad_params_err()

    # Checks if necessary flags are missing
    for flag in necessary_flags:
        if flag not in args_dict:
            bad_params_err()
    return args_dict


if __name__ == "__main__":
    args_dict = input_validation(sys.argv)

    try:
        enigma = load_enigma_from_path(args_dict['-c'])
        if '-o' in args_dict:
            with open(args_dict['-o'], 'w') as output:
                with open(args_dict['-i'], 'r') as fileInput:
                    for line in fileInput:
                        output.write(enigma.encrypt(line))
        else:
            with open(args_dict['-i'], 'r') as fileInput:
                for line in fileInput:
                    print(enigma.encrypt(line), end = '')
    except Exception:
        runtime_script_err()
