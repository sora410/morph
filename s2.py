# coding: utf-8

from math import cos, sin, radians, sqrt
from copy import copy, deepcopy
from collections import deque
from functools import reduce

# W = 500; H = 500
MAX = 1800

class ImplementationException(Exception):
    def __init__(self, arg=""):
        self.arg = arg
    
    def __str__(self):
        return "at {}".format(self.arg)

'''
class LogicDB:
    def __init__(self):
        pass
    
    def register(self, ls):
        'l1 -> l2 -> ... -> ln, where ls = [l1,l2,...,ln]'
        l = len(ls)
        assert l >= 2, 'list size must not be smaller than 2'
        for i in range(l-1):
            self.register(ls[i], ls[i+1])
    
    def register(self, a, b):
        'a -> b'
'''
        
morph = {}

class Vec:
    def __init__(self, x, y):
        self._c = complex(x, y)
    
    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def __neg__(self):
        return Vec(-self.x, -self.y)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, c):
        d = self._c * c; return Vec(d.real, d.imag)

    def __truediv__(self, v):
        '''(x,y) = (a,b)/(c,d)でuとvの座標積: (x,y) = (a*c, b*d)'''
        return Vec(self.x * v.x, self.y * v.y)

    def __floordiv__(self, v):
        '''(x,y) = (a,b)//(c,d)でuとvの座標商: (x,y) = (a/c, b/d)'''
        return Vec(self.x / v.x, self.y / v.y)

    def __copy__(self):
        return Vec(self.x, self.y)

    def __deepcopy__(self, memo):
        return Vec(self.x, self.y)

    def rot(self, deg):
        return self * complex(cos(radians(-deg)), sin(radians(-deg)))

    @property
    def r(self):
        return abs(self._c)

    @property
    def x(self):
        return self._c.real

    @property
    def y(self):
        return self._c.imag

    @staticmethod
    def d(deg):
        return Vec(1,0).rot(deg)
    
    def n(self):
        return (1/self.r) * self

    def __str__(self):
        return "({}, {})".format(self.x, self.y)


class Figure:

    '''***************** getter/setter *****************'''
    @property
    def i(self):
        return self._i
    @i.setter
    def i(self, _i):
        self._i = _i

    @property
    def o(self):
        return self._o
    @o.setter
    def o(self, _o):
        self._o = _o

    @property
    def mg(self):
        return self._mg
    @mg.setter
    def mg(self, _mg):
        self._mg = _mg

    @property
    def orig(self):
        return self._orig
    @orig.setter
    def orig(self, _orig):
        self._orig = _orig

    @property
    def vec(self):
        return self._vec
    @vec.setter
    def vec(self, _vec):
        self._vec = _vec

    @property
    def ch(self):
        return self._ch
    @ch.setter
    def ch(self, _ch):
        self._ch = _ch

    @property
    def p(self):
        return self._p
    @p.setter
    def p(self, _p):
        self._p = _p

    '''*************************************************'''

    '''initializer'''
    def __init__(self, _i=[], _o=[], _mg=[], _orig=Vec(0,0), _vec=Vec(1,1), _ch=[]):
        self._i    = _i
        self._o    = _o
        self._mg   = _mg
        self._orig  = _orig
        self._vec    = _vec
        self._ch   = _ch
        self._p = None

    def reorig(self, new):
        f = deepcopy(self); f.orig = new
        return f

    def calcunit(self):
        d = self.vec - self.orig
        u = MAX / max(d.x, d.y)
        return Vec(u, u)

    def calcoff(self):
        x, y = self.orig.x, self.orig.y
        return Vec(-x*(x < 0), -y*(y < 0))

    def draws(self, off=Vec(0,0), unit=Vec(50,50)):
#        self.draw(self.calcoff(), self.calcunit())
        self.draw(off + self.calcoff(), unit)

    def draw(self, off, unit):
        for f in self.ch:
            f.draw(off + self.orig, unit)

    '''***************** helper funcs *****************'''
    def orig_to_ac(self):
        if self.p is not None:
            tmp = self.orig + self.p.orig_to_ac()
            return tmp
        return Vec(0, 0)
#        return self.orig

    def rrc_to_ac(self, p):
        return self.orig_to_ac() + p/self.vec

    def ac_to_rrc(self, p):
        return (p - self.orig_to_ac())//self.vec

#    def yieldmg(self):
#        if self.mg:
#            tmp = self.rrc_to_ac(self.mg[0]); self.mg = self.mg[1:]
#            # tmp = self.mg[0] / self.vec; self.mg = self.mg[1:]
#            return tmp
#        for c in self.ch:
#            t = c.yieldmg()
#            if t is not None:
#                return t

    def yieldin(self):
        if self.i:
            tmp = self.i[0] / self.vec; self.i = self.i[1:]
            return tmp
        for c in self.ch:
            t = c.yieldin()
            if t is not None:
                return t + c.orig
    
    def yieldout(self):
        if self.o:
            tmp = self.o[0] / self.vec; self.o = self.o[1:]
            return tmp
        for c in self.ch:
            t = c.yieldout()
            if t is not None:
                return t + c.orig

    def yieldmg(self):
        if self.mg:
            tmp = self.mg[0] / self.vec; self.mg = self.mg[1:]
            return tmp
        for c in self.ch:
            t = c.yieldmg()
            if t is not None:
                return t + c.orig
    '''************************************************'''

    def __add__(self, other):
        ss = self.yieldmg()
        oo = other.yieldmg()
        d = ss - oo
        u, v = d.x, d.y

        if u > 0:
            if v > 0:
                s_off = Vec(0, 0);
                f_vec = Vec(max(d.x + other.vec.x, self.vec.x), max(d.y + other.vec.y, self.vec.y))
            else:
                s_off = Vec(0, -v);
                f_vec = Vec(max(d.x + other.vec.x, self.vec.x), max(s_off.y + self.vec.y, other.vec.y))
        else:
            if v > 0:
                s_off = Vec(-u, 0);
                f_vec = Vec(max(s_off.x + self.vec.x, other.vec.x), max(d.y + other.vec.y, self.vec.y))
            else:
                s_off = Vec(-u, -v); 
                f_vec = Vec(max(-d.x + self.vec.x, other.vec.x), max(-d.y + self.vec.y, other.vec.y))

        o_off = s_off + d 
        f_orig = self.orig - s_off
        s =  self.reorig(s_off); #s.mg = s.mg[1:]
        o = other.reorig(o_off); #o.mg = o.mg[1:]
        f = Figure(_orig=f_orig, _vec=f_vec, _ch=[s, o])
        s.p = f; o.p = f
        return f
            
    def __getitem__(self, p):
        f = deepcopy(self); f.mg = [p] + f.mg
        return f

    def __call__(self, *args, **kwargs):
        global morph
        for a in args:
            morph[a] = deepcopy(self)

    def __deepcopy__(self, memo):
        f = Figure(deepcopy(self.i, memo), deepcopy(self.o, memo), deepcopy(self.mg, memo))
        f.orig = deepcopy(self.orig, memo)
        f.vec  = deepcopy(self.vec, memo)
        f.ch   = deepcopy(self.ch, memo)
        f.p = deepcopy(self.p, memo)
        return f

    def __str__(self):
        s = "(in: ["
        for i in self.i:
            s += str(i) + ", "
        s += "], out: ["
        for o in self.o:
            s += str(o) + ", "
        s += "], mg: ["
        for mg in self.mg:
            s += str(mg) + ","
        s += "], ch: ["
        for c in self.ch:
            s += str(c) + ", "
        s += "], orig: " + str(self.orig) + ", vec" + str(self.vec) + ")"
        return s

class Ghost(Figure):
    def __init__(self):
        super(Ghost, self).__init__()

    def yieldin(self):
        return Vec(1/2,1/2) / self.vec

    def yieldout(self):
        return Vec(1/2,1/2) / self.vec

    def yieldmg(self):
        return Vec(1/2,1/2) / self.vec
    
    def draw(self, off, unit):
        c = Circle(self.x); c.draw(off, unit)

class Path(Figure):
    @property
    def data(self):
        return self._data

    def m(self, _m):
        self._data.append(("m", _m))
        return self

    def l(self, _l):
        self._data.append(("l", _l))
        return self

#    def z(self):
#        return self

    def __init__(self):
        super(Path, self).__init__()
        self._data = []

    def draw(self, off, unit):
        orig = (off + self.orig) / unit
        path = "M {} {}".format(orig.x, orig.y)
        for d in self.data:
            cmd, p = d; p = p / unit
            path += "{} {} {}".format(cmd, p.x, p.y)
        path += "z"
        print('''<path d="{}" stroke="black" stroke-width="1" />'''.format(path))


class Relation(Figure):
    @property
    def ls(self):
        return self._ls
    @ls.setter
    def ls(self, _ls):
        self._ls = _ls

    @property
    def path(self):
        return self._path
    @path.setter
    def path(self, _path):
        self._path = _path

    @property
    def d(self):
        return self._d
    @d.setter
    def d(self, _d):
        self._d = _d

    def __init__(self, ls, d=Vec.d(0)):
        super(Relation, self).__init__()
        self._ls = ls; self._d = d; self._path = []
        self._bewitch()
#        self._align()
    
    def _bewitch(self):
        global morph; G = Ghost()
        for i in self.ls:
            if i not in morph:
                G(i)

#    def _align(self):
#        global morph
#        l = len(self.ls); 
#        coff = Vec(0, 0); 
#        F1 = None; F2 = None
#        for i in range(l-1):
#            j = self.ls[i]; k = self.ls[i+1]
#            F1 = morph[j]; F2 = morph[k]
#            outp = F1.yieldout(); inp = F2.yieldin();
#            F1.orig = F1.orig + coff
#            # F1.draw(coff, unit);
#            P = Path(); P.orig = coff; P.m(outp).l(self.d)
#            self.path.append(P)
#            #P.draw(coff, unit);
#            # update coff
#            coff = coff + outp + self.d - inp
#        F2.orig = F2.orig + coff
#
#    def draw(self, off, unit):
#        global morph
#        for j in self.ls:
#            morph[j].draw(off, unit)
#        for p in self.path:
#            p.draw(off, unit)

    def draw(self, off, unit):
        global morph; l = len(self.ls) 
        coff = off
        F1 = None; F2 = None
        for i in range(l-1):
            j = self.ls[i]; k = self.ls[i+1]
            F1 = morph[j]; F2 = morph[k]
            F1.draw(coff, unit);
            outp = F1.yieldout(); inp = F2.yieldin();
            P = Path(); P.m(outp).l(self.d)
            P.draw(coff, unit);
            # update coff
            coff = coff + outp + self.d - inp
        F2.draw(coff, unit);

class Rect(Figure):
    def __init__(self, w, h):
        super(Rect, self).__init__(_vec=Vec(w, h))

    def draw(self, off, unit):
        orig = (off + self.orig) / unit; size = self.vec / unit
        print('''<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="black" />'''.format(x=orig.x, y=orig.y, w=size.x, h=size.y))

    def __deepcopy__(self, memo):
        r = deepcopy(super(Rect, self), memo)
        r.__class__ = self.__class__
        return r

class Circle(Figure):
    @property
    def r(self):
        return self.vec.x / 2

    def __init__(self, r):
        super(Circle, self).__init__(_vec=Vec(r, r)*2)

    def draw(self, off, unit):
        orig = (off + self.orig) / unit; size = self.vec / unit; center = orig + size * (1/2)
        print('''<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="black" />'''.format(cx=center.x, cy=center.y, r=size.x / 2))

    def __deepcopy__(self, memo):
        r = deepcopy(super(Circle, self), memo)
        r.__class__ = self.__class__
        return r

class Line(Figure):
    @property
    def l(self):
        return self.vec.r()

    def __init__(self, x, y=0):
        super(Line, self).__init__(_vec=Vec(x, y))

    def draw(self, off, unit):
        orig = (off + self.orig) / unit; end = orig + self.vec / unit
        print('''<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke-width="1" />'''.format(x1=orig.x, y1=orig.y, x2=end.x, y2=end.y))

    def __deepcopy__(self, memo):
        r = deepcopy(super(Line, self), memo)
        r.__class__ = self.__class__
        return r


def begin():
    print('''<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
    "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="{W_cm}cm" height="{H_cm}cm" viewBox="0 0 {W} {H}"
    xmlns="http://www.w3.org/2000/svg" version="1.1">
<title>a</title>'''.format(W_cm=MAX/100, H_cm=MAX/100, W=MAX, H=MAX))

def end():
    print('</svg>')

def f(fig):
    return fig[Vec(0,1)][Vec(1,1)] + fig[Vec(0,1)][Vec(0,0)] + fig[Vec(1,0)] + fig[Vec(1,0)]

def g(inc):
    r = inc.vec.x / 2
    top = Vec(1/2,0); outc = Circle((1 + 2*sqrt(3)/3) * r)
    inccc = inc[d(-60)][d(-120)] + inc[d(60)] + inc[d(120)]
    return inccc[top] + outc[top]

def h(inc):
    r = inc.vec.x / 2
    btm = Vec(1/2,1); outc = Circle((1 + 2*sqrt(3)/3) * r)
    inccc = inc[d(-60)][d(0)] + inc[d(180)] + inc[d(120)]
    return inccc[btm] + outc[btm]

def d(deg):
    return Vec(1/2,1/2) + Vec(1/2,0).rot(deg)

def sketch():
    begin()

#    r = Rect(1,1); f(r).draws();

#    ************* f2 ************
#    inc = Circle(1)
#    for i in range(6):
#        inc = g(inc) if i % 2 == 1 else h(inc)
#    inc.draws()
#    *****************************

#    re1 = Relation([1,3,5], Vec.d(0) * 3.5);
    re2 = Relation([1,2,3,4,5,6], Vec.d(0) * 2);
    
    a = Rect(1,1); a.o = [Vec(1/2,1/2)]; 
    x = Rect(1,1)[Vec(1,1/2)] + a[Vec(0,1/2)]; x.i = [Vec(0,1/2)]
    b = Rect(1,2); b.i = [Vec(0,1/4), Vec(0,3/4)]; b.mg = [Vec(1,1/4), Vec(1,3/4)]
    y = b + a[Vec(0,1/2)] + a[Vec(0,1/2)]
    
    x(2,4,5); y(1,3,6);
#    re1.draws()
    re2.draws()
    
    end()

sketch()
