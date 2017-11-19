import pdb
import lib601.sm as sm
import string
import operator


class BinaryOp:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return self.opStr + '(' + \
               str(self.left) + ', ' + \
               str(self.right) + ')'

    def eval(self, env):
        lhs = self.left.eval(env)
        rhs = self.right.eval(env)
        if isNum(lhs) and isNum(rhs):
            return self.op(lhs, rhs)

        else:
            self.left = Number(lhs) if isNum(lhs) else lhs
            self.right = Number(rhs) if isNum(rhs) else rhs
            return self

    __repr__ = __str__

class Sum(BinaryOp):
    opStr = 'Sum'
    op = operator.add

class Prod(BinaryOp):
    opStr = 'Prod'
    op = operator.mul

class Quot(BinaryOp):
    opStr = 'Quot'
    op = operator.div

class Diff(BinaryOp):
    opStr = 'Diff'
    op = operator.sub

class Assign(BinaryOp):
    opStr = 'Assign'

    def eval(self, env):
        if isNum(self.right):
            env[self.left.name] = self.right
        else:
            env[self.left.name] = self.right.eval(env)

class Number:
    def __init__(self, val):
        self.value = val

    def __str__(self):
        return 'Num(' + str(self.value) + ')'

    def eval(self, env):
        return self.value

    __repr__ = __str__

class Variable:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Var(' + self.name + ')'

    def eval(self, env):
        if self.name in env:
            if isNum(env[self.name]):
                return env[self.name]
            else:
                return env[self.name].eval(env)
        else:
            return self
        #return env[self.name]

    __repr__ = __str__


# characters that are single-character tokens
seps = ['(', ')', '+', '-', '*', '/', '=']


# Convert strings into a list of tokens (strings)
def tokenize(string):
    tokens = []
    token = ''
    i = 0

    for item in string: #Go through each item in string
        boo = False #Create flag

        while i < len(seps) and not boo: #If flag not raised and all of seps aren't checked, move forward
            if item == ' ':
                if token == '': #If nothing is in token, just ignore the space
                    i = 0
                    boo = True

                else:
                    tokens.append(token)
                    token = ''
                    i = 0
                    boo = True

            elif item != seps[i]: #If item not the same as seps[i], check next seps[i]
                i = i + 1
                if i == len(seps): #If all of seps have been checked and no match, add item to token
                    token = token + item
                    i = 0
                    boo = True

            elif item == seps[i]: #If item is the same as seps[i]...
                if token != '': #If token has items in it, append token then append item, then raise flag, clear token, and start count over
                    tokens.append(token)
                    tokens.append(item)
                    token = ''
                    i = 0
                    boo = True

                else: #If token has no item in it, append item, raise flag, and start count over
                    tokens.append(item)
                    i = 0
                    boo = True

    if token != '': #Need this condition in case NO tokens are found
        tokens = token

    return tokens



# tokens is a list of tokens
# returns a syntax tree:  an instance of {\tt Number}, {\tt Variable},
# or one of the subclasses of {\tt BinaryOp}
def parse(tokens):
    def parseExp(index):
        if numberTok(tokens[index]):
            return Number(float(tokens[index])), index + 1
        elif variableTok(tokens[index]):
            return Variable(tokens[index]), index + 1
        elif tokens[index] is "(":
            lhs, next_index = parseExp(index + 1)
            op = tokens[next_index]
            rhs, next_index = parseExp(next_index + 1)
            if op is '+':
                op = Sum(lhs, rhs)
            elif op is '-':
                op = Diff(lhs, rhs)
            elif op is '*':
                op = Prod(lhs, rhs)
            elif op is '/':
                op = Quot(lhs, rhs)
            elif op is '=':
                op = Assign(lhs, rhs)
            return op, next_index + 1

    (parsedExp, nextIndex) = parseExp(0)
    return parsedExp


# token is a string
# returns True if contains only digits
def numberTok(token):
    for char in token:
        if not char in string.digits: return False
    return True


# token is a string
# returns True its first character is a letter
def variableTok(token):
    for char in token:
        if char in string.letters: return True
    return False


# thing is any Python entity
# returns True if it is a number
def isNum(thing):
    return type(thing) == int or type(thing) == float


# Run calculator interactively
def calc():
    env = {}
    while True:
        e = raw_input('%')  # prints %, returns user input
        print '%',  str(parse(tokenize(e)).eval(env))
        print '   env =', env


# exprs is a list of strings
# runs calculator on those strings, in sequence, using the same environment
def calcTest(exprs):
    env = {}
    for e in exprs:
        print '%', e  # e is the experession
        print  str(parse(tokenize(e)).eval(env))
        print '   env =', env


# Simple tokenizer tests
'''Answers are:
['fred']
['777']
['777', 'hi', '33']
['*', '*', '-', ')', '(']
['(', 'hi', '*', 'ho', ')']
['(', 'fred', '+', 'george', ')']
['(', 'hi', '*', 'ho', ')']
['(', 'fred', '+', 'george', ')']
'''


def testTokenize():
    print tokenize('fred ')
    print tokenize('777 ')
    print tokenize('777 hi 33 ')
    print tokenize('**-)(')
    print tokenize('( hi * ho )')
    print tokenize('(fred + george)')
    print tokenize('(hi*ho)')
    print tokenize('( fred+george )')


# Simple parsing tests from the handout
'''Answers are:
Var(a)
Num(888.0)
Sum(Var(fred), Var(george))
Quot(Prod(Var(a), Var(b)), Diff(Var(cee), Var(doh)))
Quot(Prod(Var(a), Var(b)), Diff(Var(cee), Var(doh)))
Assign(Var(a), Prod(Num(3.0), Num(5.0)))
'''


def testParse():
    print parse(['a'])
    print parse(['888'])
    print parse(['(', 'fred', '+', 'george', ')'])
    print parse(['(', '(', 'a', '*', 'b', ')', '/', '(', 'cee', '-', 'doh', ')', ')'])
    print parse(tokenize('((a * b) / (cee - doh))'))
    print parse(tokenize('(a = (3 * 5))'))


####################################################################
# Test cases for EAGER evaluator
####################################################################

def testEval():
    env = {}
    Assign(Variable('a'), Number(5.0)).eval(env)
    print Variable('a').eval(env)
    env['b'] = 2.0
    print Variable('b').eval(env)
    env['c'] = 4.0
    print Variable('c').eval(env)
    print Sum(Variable('a'), Variable('b')).eval(env)
    print Sum(Diff(Variable('a'), Variable('c')), Variable('b')).eval(env)
    Assign(Variable('a'), Sum(Variable('a'), Variable('b'))).eval(env)
    print env #added line...
    print Variable('a').eval(env)
    print env


# Basic calculator test cases (see handout)
testExprs = ['(2 + 5)',
             '(z = 6)',
             'z',
             '(w = (z + 1))',
             'w'
             ]
# calcTest(testExprs)

####################################################################
# Test cases for LAZY evaluator
####################################################################

# Simple lazy eval test cases from handout
'''Answers are:
Sum(Var(b), Var(c))
Sum(2.0, Var(c))
6.0
'''


def testLazyEval():
    env = {}
    Assign(Variable('a'), Sum(Variable('b'), Variable('c'))).eval(env)
    print Variable('a').eval(env)
    env['b'] = Number(2.0)
    print Variable('a').eval(env)
    env['c'] = Number(4.0)
    print Variable('a').eval(env)


# Lazy partial eval test cases (see handout)
lazyTestExprs = ['(a = (b + c))',
                 '(b = ((d * e) / 2))',
                 'a',
                 '(d = 6)',
                 '(e = 5)',
                 'a',
                 '(c = 9)',
                 'a',
                 '(d = 2)',
                 'a']
# calcTest(lazyTestExprs)

## More test cases (see handout)
partialTestExprs = ['(z = (y + w))',
                    'z',
                    '(y = 2)',
                    'z',
                    '(w = 4)',
                    'z',
                    '(w = 100)',
                    'z']

# calcTest(partialTestExprs)
