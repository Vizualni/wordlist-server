#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor, protocol


def memoize(f):
    """ Memoization decorator for functions taking one or more arguments. """
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args):
            return self[args]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret
    return memodict(f)

class Node():

    def __init__(self, letter, is_end=False, parent=None):
        self.letter = letter.lower()
        self.end = is_end
        self.next = {}
        self.parent = parent

    def add_next(self, node):
        self.next[node.get_letter()] = node

    def get_letter(self):
        return self.letter

    def get_next_list(self):
        return self.next

    def is_in(self, letter):
        return letter.lower() in self.next

    def get_or_set(self, letter):
        if self.is_in(letter):
            return self.get_node_with_letter(letter)
        node = Node(letter, parent=self)
        self.add_next(node)
        return node

    def set_ending_letter(self):
        self.end = True

    def get_word(self):
        if not self.is_ending():
            return None
        letters = []
        node = self
        while node:
            letters.append(node.get_letter())
            node = node.parent
        return ''.join(letters[::-1])

    def is_ending(self):
        return self.end

    def get_node_with_letter(self, letter):
        if self.is_in(letter):
            return self.next[letter.lower()]
        return None

    def __str__(self):
        return '<Node {} >: {}'.format(self.get_letter(), ', '.join(self.get_next_list().keys()))

def create_trie(wordlist):
    root = Node('')
    for word in wordlist:
        tmp_root = root
        for letter in word:
            tmp_root = tmp_root.get_or_set(letter)
        tmp_root.set_ending_letter()
    return root

def is_word_in(trie, word):
    node = trie
    for letter in word:
        node = node.get_node_with_letter(letter)
        if not node:
            return False
    return node.is_ending()

def levenstain_distance(trie, word, max_cost):

    def levenstain_wrapper(node, word, letter, max_cost, result, rowBefore):
        row = [rowBefore[0] + 1]
        columns = len(word) + 1
        for column in xrange(1, columns):
            row.append(min([row[column - 1] + 1, rowBefore[column] + 1, rowBefore[column - 1] + (1 if word[column - 1] != letter else 0)]))
        if row[-1]<=max_cost and node.is_ending() == True:
            result.append( (node.get_word(), row[-1]) )
        if min(row) <= max_cost:
            for letter in node.get_next_list().keys():
                levenstain_wrapper(node.get_node_with_letter(letter), word, letter, max_cost, result, row)

    result = []
    row = range(len(word) + 1)
    for letter in trie.get_next_list().keys():
        levenstain_wrapper(trie.get_node_with_letter(letter), word, letter, max_cost, result, row)
    return result


f = open('../wordlist.txt', 'r')
trie = create_trie(f.read().split("\n")[:])
print "Done creating trie"

class WordlistServer(protocol.Protocol):


    def dataReceived(self, data):
        distance, word = data.split(' ')
        distances = levenstain_distance(trie, word.strip(), int(distance))
        if not distances:
            self.transport.write('null\n')
        else:
            self.transport.write(','.join([str(x) for x in distances]) + '\n')


if __name__=='__main__':

    """This runs the protocol on port 8000"""
    factory = protocol.ServerFactory()
    factory.protocol = WordlistServer
    reactor.listenTCP(1313, factory)
    reactor.run()
