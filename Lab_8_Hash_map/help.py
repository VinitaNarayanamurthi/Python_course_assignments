from collections import namedtuple
import random
import re

Entry = namedtuple('Entry', ('key', 'value'))
ShuffleMap = list(range(0, 65536))
random.shuffle(ShuffleMap)

'''
To make sure that the DELETED sentinel does not match
anything we actually want to have in the table, make it
a unique (content-free!) object.
'''


class _delobj: pass


DELETED = Entry(_delobj(), None)


class Hashmap:
    __slots__ = (
        'table',
        'numkeys',
        'cap',
        'maxload',
        'collision',
        'probe',
        'hash_func'
    )

    def __init__(self, hash_func=hash, initsz=100, maxload=0.7):
        '''
        Creates an open-addressed hash map of given size and maximum load factor
        :param hash_func: hash function (default python's builtin hash function)
        :param initsz: Initial size (default 100)
        :param maxload: Max load factor (default 0.7)
        '''
        self.cap = initsz
        self.table = [None for _ in range(self.cap)]
        self.numkeys = 0
        self.maxload = maxload
        self.collision = 0
        self.probe = 0
        self.hash_func = hash_func

    def put(self, key, value):
        '''
        Adds the given (key,value) to the map, replacing entry with same key if
        present.
        :param key: Key of new entry
        :param value: Value of new entry
        '''
        index = self.hash_func(key) % self.cap

        # collision happens at the first try of the insertion
        if self.table[index] is not None and self.table[index] != DELETED:
            self.collision += 1

        self.probe += 1
        while self.table[index] is not None and \
                        self.table[index] != DELETED and \
                        self.table[index].key != key:
            index += 1
            self.collision += 1
            self.probe += 1

            if index == len(self.table):
                index = 0

        if self.table[index] is None:
            self.numkeys += 1

        self.table[index] = Entry(key, value)

        if self.numkeys / self.cap > self.maxload:
            # rehashing
            oldtable = self.table
            # refresh the table
            self.cap *= 2
            self.table = [None for _ in range(self.cap)]
            self.numkeys = 0
            # put items in new table
            for entry in oldtable:
                if entry is not None:
                    self.put(entry[0], entry[1])

    def remove(self, key):
        '''
        Remove an item from the table
        :param key: Key of item to remove
        :return: Value of given key
        '''
        index = self.hash_func(key) % self.cap
        while self.table[index] is not None and self.table[index].key != key:
            index += 1
            if index == len(self.table):
                index = 0
        if self.table[index] is not None:
            self.table[index] = DELETED


    def get(self, key):
        '''
        Return the value associated with the given key
        :param key: Key to look up
        :return: Value (or KeyError if key not present)
        '''
        index = self.hash_func(key) % self.cap
        self.probe += 1

        while self.table[index] is not None and self.table[index].key != key:
            index += 1
            self.probe += 1

            if index == self.cap:
                index = 0

        if self.table[index] is not None:
            return self.table[index].value
        else:
            raise KeyError('Key ' + str(key) + ' not present')

    def contains(self, key):
        '''
        Returns True/False whether key is present in map
        :param key: Key to look up
        :return: Whether key is present (boolean)
        '''
        index = self.hash_func(key) % self.cap
        self.probe += 1

        while self.table[index] is not None and self.table[index].key != key:
            index += 1
            self.probe += 1

            if index == self.cap:
                index = 0

        return self.table[index] is not None


def listOfWords(filename):
    """
    Open a file and return a list of every words in the file.
    :param filename:    the file name
    :return:    a list of words
    """
    file = open(filename, 'r')
    words = []

    for line in file:
        # remove punctuations
        l = re.split('\W+', line)

        # remove all empty item in the list
        for _ in range(l.count('')):
            l.remove('')

        # convert every words into lower case
        for i in range(len(l)):
            l[i] = str(l[i]).lower()

        # extend the list with the words list of this line
        words.extend(l)

    file.close()
    return words


def hashMidSquare(key, r=4):
    """
    Hash the key with the "Mid-Square" method
    :param key:   the key to the hash function
    :param r:   number of mid-digits to be used for hashing
    :return    a hash value
    """
    value = sum([ord(c) * 8 ** i for i, c in enumerate(key)])
    value = value % 10 ** (r * 2)
    valueSquare = value ** 2
    startDigit = r * 3 / 2 + 1
    midValue = int(
        ("{:0" + str(r * 4) + "d}").format(valueSquare)[
        startDigit:startDigit + 4
        ]
    )
    return midValue
