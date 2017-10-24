import sys
import re
import fsm

from random import choice


class Thing:
    def __init__(self,name):
        self.greeting = "Hello"
        self.name = name
    def __str__(self):
        return self.mymethod()

    def mymethod(self):
        return "%s" % self.greeting


def main():
    people = {'A':True, 'B':False}
    randx = choice(0,1)
    print(randx)
    pass



if __name__ == "__main__":
    main()
