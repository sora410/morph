# coding: utf-8

from math import cos, sin, radians, sqrt
from copy import copy, deepcopy
from collections import deque

W = 500; H = 500
MAX = 800

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

    def r(self):
        return abs(self._c)

    @property
    def x(self):
        return self._c.real

    @property
    def y(self):
        return self._c.imag

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

    def draw(self, off=None, unit=None):
        if off is None:
            off  = self.calcoff();
        if unit is None:
            unit = self.calcunit();
        for f in self.ch:
            f.draw(off + self.orig, unit)

    '''***************** helper funcs *****************'''
    def orig_to_ac(self):
        if self.p is not None:
            return self.orig + self.p.orig_to_ac()
        # return self.orig
        return Vec(0, 0)

    def rrc_to_ac(self, p):
        return self.orig_to_ac() + p/self.vec

    def ac_to_rrc(self, p):
        return (p - self.orig_to_ac())//self.vec

    def yieldmg_ac(self):
        if self.mg:
            tmp = self.rrc_to_ac(self.mg[0]); self.mg = self.mg[1:]
            # tmp = self.mg[0] / self.vec; self.mg = self.mg[1:]
            return tmp
        for c in self.ch:
            t = c.yieldmg_ac()
            if t is not None:
                return t
    '''************************************************'''

    def __add__(self, other):
        # d = other.nextmg_ac() - self.nextmg_ac()
        ss = self.yieldmg_ac()
        oo = other.yieldmg_ac()
        d = ss - oo

        # d = other.yieldmg_ac() - self.yieldmg_ac() 
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

    def __deepcopy__(self, memo):
        f = Figure(deepcopy(self.i, memo), deepcopy(self.o, memo), deepcopy(self.mg, memo))
        f.orig = deepcopy(self.orig, memo)
        f.vec  = deepcopy(self.vec, memo)
        f.ch   = deepcopy(self.ch, memo)
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

class Rect(Figure):
    def __init__(self, w, h):
        super(Rect, self).__init__(_vec=Vec(w, h))

    def draw(self, off=Vec(0,0), unit=None):
        if unit is None:
            unit = self.calcunit()
        orig = (off + self.orig) / unit; size = self.vec / unit
        print('''<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="black" />'''.format(x=orig.x, y=orig.y, w=size.x, h=size.y))

    def __deepcopy__(self, memo):
        r = deepcopy(super(Rect, self), memo)
        r.__class__ = self.__class__
        return r

class Circle(Figure):
    def __init__(self, r):
        super(Circle, self).__init__(_vec=Vec(r, r)*2)

    def draw(self, off=Vec(0,0), unit=None):
        if unit is None:
            unit = self.calcunit()
        orig = (off + self.orig) / unit; size = self.vec / unit; center = orig + size * (1/2)
        print('''<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="black" />'''.format(cx=center.x, cy=center.y, r=size.x / 2))

    def __deepcopy__(self, memo):
        r = deepcopy(super(Circle, self), memo)
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

def d(deg):
    return Vec(1/2,1/2) + Vec(1/2,0).rot(deg)

def sketch():
    begin()
    top = Vec(1/2,0)
    inc = Circle(1); outc = Circle(1 + 2*sqrt(3)/3)
    inccc = inc[d(-60)][d(-120)] + inc[d(60)] + inc[d(120)]
    c = inccc[top] + outc[top]
    c.draw()

#    a = r[Vec(1/3,1)] + r[Vec(11/12,0)]
#    a.draw()
#    inc = r
#    (inc[d(-60)] + inc[d(120)]).draw()
    
#    inccc = inc[d(0)] + inc[d(-120)][d(180)] + inc[d(60)]
#    print(inccc.vec)
#    inccc.draw()
#    t = r[Vec(1,11/12)] + inc[d(-120)][d(180)] + inc[d(0)][d(60)] + inc[d(180)]
#    t.draw()

    #inccc.draw()
    
#    c = inc[d(-120)] + inc[d(0)][d(60)] + inc[d(180)]
#    c.draw()

#    a = inc[d(-60)][d(-120)] + inc[d(60)]
#    print(a)
#    a.draw()
#    r = Rect(1,1);
#    top = Vec(1/2,0); btm = Vec(1/2,1); lft = Vec(0,1/2); rht = Vec(1,1/2)
    # rr = r[Vec(1,1/2)] + r[Vec(1/2,1)][Vec(0,1/2)] + r[Vec(1/2,0)]
    #e = r[lft][top] + r[rht][btm]
#    f = r[btm] + r[top]
#    f.draw();
#    (e + e).draw()
    end()

sketch()
