from sympy import nextprime
import random

'''
Before you start: Read the README 
'''

# ----- Helper Classes (Do not edit) -----

# Node class for the linked list
class Node:
    def __init__(self, key, value, next=None):
        self.key = key
        self.value = value
        self.next = next

# Implements the common h(x) = x mod m 
class DeterministicHash:
    def __init__(self, U, m):
        self.U = U
        self.m = m

    # Returns h(x)
    def evaluate(self, x): 
        return x% self.m

# Implements h_{a,b}(x)=((ax+b) mod p) mod m)
class RandomHash:
    def __init__(self, U, m, seed=None):
        self.U = U
        self.m = m
        if seed is not None:
            random.seed(seed)
        self.p = nextprime(U)
        self.a = random.randrange(0, self.p)
        self.b = random.randrange(0, self.p)

    def evaluate(self, x):
        return ((self.a * x + self.b) % self.p) % self.m


# ----- Hash Table Class (Problem 1a) -----

class HashTable:

    # Initializes the hash table
    #   U: (int) Universe for keys
    #   m : (int) size of the hash table
    #   optimize: bool : toggle optimizization "HashTable," implementing search and delete (return or delete the key-value pair)

    def __init__(self, U, m, hash_function, lazing):
        self.U = U
        self.m = m
        self.hash_function = hash_function
        self.lazing = lazing
        self.table = [None] * m 

    '''
    Helper function to compute the bucket index for a given key
    '''
    def _bucket_index(self, key):
        return self.hash_function.evaluate(key)

    '''
    Inserts (key, value) into the table.
    Always inserts at the head of the list for O(1) insertion.
    '''
    def insert(self, key, value):
        idx = self._bucket_index(key)
        node = Node(key, value, self.table[idx])
        self.table[idx] = node
        return self

    '''
    Searches for key and returns the associated value or None.

    lazing == True:
        Return the VALUE at the HEAD of bucket h(key), even if keys don't match.
        (Intentional "optimization" that can be wrong, per assignment.)
    lazing == False:
        Traverse the chain and return the value for the first node
        with node.key == key; return None if not found.
    '''
    def search(self, key): 
        idx = self._bucket_index(key)
        head = self.table[idx]

        if self.lazing:
            if head is None:
                return None
            return head.value
        else:
            # TODO: Implement search for opt=False
            return None
    
    '''
    Deletes key from the table.
    Returns True if a node was removed, else False.

    lazing == True:
        Delete the HEAD of bucket h(key), regardless of key match.
    lazing == False:
        Traverse and remove the first node with node.key == key.
    '''
    def delete(self, key):
        idx = self._bucket_index(key)

        if self.lazing:
            if self.table[idx] is None:
                return False
            self.table[idx] = self.table[idx].next
            return True
        else:
            # TODO: Implement delete for opt=False
            return False
