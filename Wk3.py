import lib601.sm as sm

class Cascade(sm.SM):
    def __init__(self, sm1, sm2):
        self.sm1 = sm1
        self.sm2 = sm2
        self.startState = (self.sm1.startState, self.sm2.startState)

    def getNextValues(self, state, inp):
        (s1, s2) = state
        (newS1, o1) = self.sm1.getNextValues(s1, inp)
        (newS2, o2) = self.sm2.getNextValues(s2, o1)
        print"CASCADE:"
        print "sm1: ", self.sm1
        print "sm2: ", self.sm2
        print "newS1: ", newS1
        print "newS2: ", newS2
        print "o1: ", o1
        print "o2: ", o2
        print "\n"
        return ((newS1, newS2), o2)

class Parallel(sm.SM):
    def __init__(self, sm1, sm2):
        self.sm1 = sm1
        self.sm2 = sm2
        self.startState = (sm1.startState, sm2.startState)

    def getNextValues(self, state, inp):
        (s1, s2) = state
        (newS1, o1) = self.sm1.getNextValues(s1, inp)
        (newS2, o2) = self.sm2.getNextValues(s2, o1)
        return((newS1, newS2), (o1, o2))

class Parallel2(sm.SM):
    def __init__(self, sm1, sm2):
        self.sm1 = sm1
        self.sm2 = sm2
        self.startState = (sm1.startState, sm2.startState)

    def getNextValues(self, state, inp):
        (s1, s2) = state
        (i1, i2) = sm.splitValue(inp)
        (newS1, o1) = self.sm1.getNextValues(s1, i1)
        (newS2, o2) = self.sm2.getNextValues(s2, i2)
        print "PARALLEL2:"
        print "i1: ", i1
        print "i2: ", i2
        print "newS1: ", newS1
        print "newS2: ", newS2
        print "o1: ", o1
        print "o2: ", o2
        print "\n"
        return ((newS1, newS2), (o1, o2))

class PureFunction(sm.SM):
    def __init__(self, f):
        self.f = f
        self.startState = 0

    def getNextValues(self, state, inp):
        out = self.f(inp)
        return (out, out)

def cascade():
    sm1 = sm.Delay(1)
    sm2 = PureFunction(mult)

    c = Cascade(sm1, sm2)
    o = c.transduce([1,3,7,2])
    return o

def mult(x):
    return(x*2)

class Adder(sm.SM):
    def getNextState(self, state, inp):
        (i1, i2) = sm.splitValue(inp)
        return sm.safeAdd(i1, i2)

class BA1(sm.SM):
    def __init__(self):
        self.startState = 0
    def getNextValues(self, state, inp):
        if inp != 0:
            newState = state * 1.02 + inp - 100
        else:
            newState = state * 1.02
        return (newState, newState)

class BA2(sm.SM):
    def __init__(self):
        self.startState = 0
    def getNextValues(self,state, inp):
        newState = state * 1.01 + inp
        return (newState, newState)

class maxAccount(sm.SM):
    def __init__(self):
        self.sm1 = BA1
        self.sm1_inst = BA1()
        self.sm2 = BA2
        self.sm2_inst = BA2()

    def getNextValues(self, state, inp):
        (s1,s2) = state
        self.ba1 = PureFunction(self.sm1_inst.getNextValues)
        self.ba2 = PureFunction(self.sm2_inst.getNextValues)
        self.double_bank = sm.Parallel(self.ba1, self.ba2)
        ((newS1, newS2), (o1, o2)) = self.double_bank.getNextValues((s1,s2), inp)
        if newS1 > newS2:
            return newS1
        else:
            return newS2

class maxAccount2(sm.SM):
    def __init__(self):
        self.sm1 = BA1
        self.sm1_inst = BA1()
        self.sm2 = BA2
        self.sm2_inst = BA2()

    def getNextValues(self, state, inp):
        (s1, s2) = state
        self.ba1 = PureFunction(self.sm1_inst.getNextValues)
        self.ba2 = PureFunction(self.sm2_inst.getNextValues)
        self.double_bank = sm.Parallel(self.ba1, self.ba2)
        ((newS1, newS2), (o1, o2)) = self.double_bank.getNextValues((s1, s2), inp)
        if newS1 > newS2:
            return newS1
        else:
            return newS2

class switchAccount(sm.SM):
    def __init__(self):
        self.sm1 = BA1
        self.sm1_inst = BA1()
        self.sm2 = BA2
        self.sm2_inst = BA2()
        self.ba1 = PureFunction(self.sm1_inst.getNextValues)
        self.ba2 = PureFunction(self.sm2_inst.getNextValues)
        self.double_bank = sm.Cascade(sm.Parallel2(self.ba1, self.ba2), Adder())
        self.startState = (0, 0)
    def getNextValues(self, state, inp):
        if inp > 3000:
            (s1, s2) = state
            return self.double_bank.getNextValues((s1, s2), (inp, 0))
        else:
            (s1, s2) = state
            return self.double_bank.getNextValues((s1, s2), (0, inp))

def test_switch(state, inp):
    return switchAccount().getNextValues(state, inp)

def test_max(state, inp):
    (s1, s2) = state
    return sm.Parallel(BA1().getNextValues(s1,inp), BA2().getNextValues(s2,inp))

class SumTSM(sm.SM):
    startState = (0,0)

    def getNextValues(self, state, inp):
        (count, total) = state
        if count == 100:
            return ((count+1, total+inp), total + inp)
        else:
            return ((count+1, total+inp), None)

    def done(self, state):
        (count, total) = state
        return count == 101

def test_sumtsm():
    x = [1,2]*101
    c = SumTSM()
    c.transduce(x, verbose = True)

class ConsumeFiveValues(sm.SM):

    startState = (0, 0) # count, total

    def getNextValues(self, state, inp):
        (count, total) = state
        if count == 4:
            return ((count + 1, total + inp), total + inp)

        else:
            return ((count + 1, total + inp), None)

    def done(self, state):
        (count, total) = state
        return count == 5

class CharTSM (sm.SM):
    startState = False
    def __init__(self, c):
        self.c = c
    def getNextValues(self, state, inp):
        return (True, self.c)
    def done(self, state):
        return state

class Repeat (sm.SM):
    def __init__(self, sm, n = None):
        self.sm = sm
        self.startState = (0, self.sm.startState)
        self.n = n

    def advanceIfDone(self, counter, smState):
        while self.sm.done(smState) and not self.done((counter, smState)):
            counter = counter + 1
            smState = self.sm.startState
        return (counter, smState)

    def getNextValues(self, state, inp):
        (counter, smState) = state
        (smState, o) = self.sm.getNextValues(smState, inp)
        (counter, smState) = self.advanceIfDone(counter, smState)
        return ((counter, smState), o)

    def done(self, state):
        (counter, smState) = state
        return counter == self.n

class Sequence (sm.SM):
    def __init__(self, smList):
        self.smList = smList
        self.startState = (0, self.smList[0].startState)
        self.n = len(smList)

    def advanceIfDone(self, counter, smState):
        while self.smList[counter].done(smState) and counter + 1 < self.n:
            counter = counter + 1
            smState = self.smList[counter].startState
        return (counter, smState)

    def getNextValues(self, state, inp):
        (counter, smState) = state
        (smState, o) = self.smList[counter].getNextValues(smState, inp)
        (counter, smState) = self.advanceIfDone(counter, smState)
        return ((counter, smState), o)

    def done(self, state):
        (counter, smState) = state

        return self.smList[counter].done(smState)

def fourTimes():
    x = [1,2]*400
    return Repeat(SumTSM(),4).transduce(x)

class CountUpTo(sm.SM):

    startState = 0

    def __init__(self, inp):
        self.n = inp

    def getNextValues(self, state, inp):
        state = state + 1
        return (state, state)

    def done(self, state):
        return state == self.n

def testCUT():
    sm = CountUpTo(3)
    return sm.run(n=20)

def makeSequenceCounter(inp):
    return Sequence([CountUpTo(n) for n in inp])

def sq(x):
    return x*x

def mapList(proc, list):
    smList = [None]*len(list)
    for n in range(0, len(list)):
        smList[n] = PureFunction(proc)
    return [smList[list.index(n)].getNextValues(n,n)[1] for n in list]

def testmapList():
    x = sq
    return mapList(x, [1,1,3,4,1,3,1,2])