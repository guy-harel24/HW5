import copy
import json

W1_IDX = 0
W2_IDX = 1
W3_IDX = 2

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
        # Local variables
        W1_MULT = 2
        DEFINED_MOD = 26

        # Check if encryption is not needed
        if char.islower() is False:
            result = (char, 0)
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
        result = (c3, 1)
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
    else: tmp_wheels[W3_IDX] = 0


class JSONFileError(Exception):
    def __init__(self, message="JSONFileError occurred"):
        self.message = message
        super().__init__(self.message)


def load_enigma_from_path(path):
    try:
        with open(path, 'r') as file:
            maps = json.load(file)
    except Exception:
        raise JSONFileError(path)

    hash_map = maps['hash_map']
    wheels = maps['wheels']
    reflector_map = maps['reflector_map']
    return Enigma(hash_map, wheels, reflector_map)
