__author__ = 'madanrp'

import re

def is_number(str):
    try:
        int(str)
        return True
    except Exception as e:
        return False

def is_valid_variable(str):
    return re.match('^[\w]+$', str) is not None

class Database:
    def __init__(self):
        self._data = {}
        self._transactions = []
        self._value_dict = {}

    def _validate_set(self, command):
        assert(len(command) == 3)
        assert(command[0] == "SET")
        assert(is_number(command[2]))
        assert(is_valid_variable(command[1]))

    def _validate_get(self, command):
        assert(len(command) == 2)
        assert(command[0] == "GET")
        assert(is_valid_variable(command[1]))

    def _validate_numequalto(self, command):
        assert(len(command) == 2)
        assert(command[0] == "NUMEQUALTO")
        assert(is_number(command[1]))

    def validate_command(self, tokens):
        if tokens[0] == "SET":
            self._validate_set(tokens)
        elif tokens[0] == "GET":
            self._validate_get(tokens)
        elif tokens[0] == "NUMEQUALTO":
            self._validate_numequalto(tokens)
        elif tokens[0] in ["BEGIN", "END", "ROLLBACK", "COMMIT"]:
            assert(len(tokens) == 1)

    def split(self, command_str):
        return command_str.strip().split()

    def _set_value(self, name, value):
        curr_val = self._data.get(name, None)
        if curr_val:
            self._value_dict[curr_val] -= 1

        self._data[name] = value
        self._value_dict[value] = self._value_dict.get(value, 0) + 1

    def set(self, name, value):
        curr_val = self._data.get(name, None)
        self._add_transaction(name, "SET", curr_val, value)
        self._set_value(name, value)

    def get(self, name):
        val = self._data.get(name, None)
        if val is None:
            val = "NULL"
        print val

    def _add_transaction(self, name, command, before_val, after_val):
        if len(self._transactions) < 1:
            return

        current_trasaction = self._transactions[-1]
        current_trasaction.append((name, command, before_val, after_val))

    def unset(self, name):
        curr_val = self._data.get(name, None)
        if curr_val:
            self._value_dict[curr_val] -= 1
        self._add_transaction(name, "UNSET", curr_val, None)
        self._data.pop(name)

    def begin(self):
        self._transactions.append([])

    def commit(self):
        if len(self._transactions) < 1:
            print "NO TRANSACTION"
            return

        self._transactions = []

    def rollback(self):
        if len(self._transactions) < 1:
            print "NO TRANSACTION"
            return

        last_transaction = self._transactions[-1]
        for action in reversed(last_transaction):
            name, command, before_val, after_val = action
            if command == "SET":
                self._set_value(name, before_val)
            elif command == "UNSET":
                self._set_value(name, before_val)
        self._transactions.pop()

    def num_equal_to(self, value):
        print self._value_dict.get(value, 0)

    def handle_command(self, command):
        tokens = self.split(command)
        self.validate_command(tokens)
        if tokens[0] == "SET":
            print tokens
            self.set(tokens[1], int(tokens[2]))
        elif tokens[0] == "UNSET":
            self.unset(tokens[1])
        elif tokens[0] == "NUMEQUALTO":
            self.num_equal_to(int(tokens[1]))
        elif tokens[0] == "BEGIN":
            self.begin()
        elif tokens[0] == "COMMIT":
            self.commit()
        elif tokens[0] == "ROLLBACK":
            self.rollback()
        elif tokens[0] == "GET":
            self.get(tokens[1])
        else:
            raise Exception("Invalid command %s" % (tokens[0]))

if __name__ == "__main__":
    database = Database()
    command = raw_input()
    while command.strip() != "END":
        database.handle_command(command)
        command = raw_input()

