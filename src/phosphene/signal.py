import pdb
from util import *
import time
__all__ = ['Signal', 'lift', 'foldp', 'perceive']

class lift:
    """ Annotate an object as lifted """
    def __init__(self, obj, idxable=None):
        self.obj = obj
        self.type = ['list', 'lambda'][hasattr(obj, '__call__')]
        self.indexable = idxable

    def manifest(self, sig):
        # manifest in a process.
        if self.type == "lambda":
            return self.obj(sig)
        else:
            # assuming this is a list type
            if self.indexable is None or self.indexable == True:
                # Make the array temporally indexable
                return indexable(self.obj, sig.x)
            elif indexable == False:
                return self.obj[sig.x]

def foldp(f, sig, init):
    """ takes a function, a time varying value, initial value
      and reduces it over time"""
    val = init
    def g(sig):
        val = f(sig, val)
        return val
    return lift(g)

class Signal:
    """ The Signal abstraction. """
    def __init__(self, Y, sF, prefFps=90):
        self.Y = Y
        self.x = 0
        self.fps = 0
        self.prefFps = prefFps
        self.sF = sF
        self.lifts = {}
        self.t = lift(lambda s: s.time())
        self.cache = {}

    def time(self, t=time.time):
        # this sig's definition of time
        return t()
    def __getattr__(self, k):
        # call the thing that is requred with self
        if self.lifts.has_key(k):
            # Lifted values must have the same value
            # for the same x. Cache them.
            # This also helps in performance e.g. when
            # fft is needed a multiple places

            if self.cache.has_key(k):
                x, val = self.cache[k]

                if x == self.x:
                    return val

            val = self.lifts[k].manifest(self)
            self.cache[k] = (self.x, val)
            return val
        else:
            return self.__dict__[k]

    def __setattr__(self, k, v):
        if isinstance(v, lift):
            self.lifts[k] = v
        else:
            self.__dict__[k] = v

    def advance(self, x, fps):
        self.x = x
        self.fps = fps

def perceive(processes, sig, prefFps):
    # LOL. Profound name and shit.
    start = sig.time()
    callSpacing = 1.0 / prefFps
    nY = len(sig.Y)
    prev_x = -1
    x = 0
    while x <= nY:
        tic = sig.time()
        x = int((tic-start) * sig.sF)
        # Loop.
        sig.advance(x, sig.sF / float(x - prev_x))
        # Process all the processes
        for p in processes:
                p(sig)
        prev_x = x
        # atrocious assumptions, but they'll serve the purpose
        toc = sig.time()
        wait = (tic + callSpacing - toc)
        # chill out before looping.
        if wait > 0: time.sleep(wait)