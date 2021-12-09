# coding: utf-8

from math import cos, sin, radians, sqrt
from copy import copy, deepcopy
from collections import deque, defaultdict
from functools import reduce
import enum

# W = 500; H = 500
MAX = 1800

@enum.unique
class Ver(enum.Enum):
    top = 0
    mid = 1
    bottom = 2

@enum.unique
class Hor(enum.Enum):
    left = 0
    mid = 1
    right = 2

class ImplementationException(Exception):
    def __init__(self, arg=""):
        self.arg = arg
    
    def __str__(self):
        return "at {}".format(self.arg)

morph = defaultdict(lambda: Ghost())

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

UNIT = Vec(50,50)

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

    def draws(self, off=Vec(0,0), unit=UNIT):
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
            # morph[a] = self.reorig(morph[a].orig)
            # ↓ is really good?
            morph[a] = self.reorig(morph[a].orig + self.orig)

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
        self.c = Circle(1/2)

    def yieldin(self):
        return Vec(1/2,1/2) / self.c.vec

    def yieldout(self):
        return Vec(1/2,1/2) / self.c.vec

    def yieldmg(self):
        return Vec(1/2,1/2) / self.c.vec
    
    def draw(self, off, unit):
        self.c.orig = self.orig
        self.c.draw(off, unit)

    def __deepcopy__(self, memo):
        r = deepcopy(super(Ghost, self), memo)
        r.__class__ = self.__class__
        r.c = deepcopy(self.c)
        return r

class Path(Figure):
    @property
    def data(self):
        return self._data

    @property
    def mstart(self):
        return self._mstart
    @mstart.setter
    def mstart(self, _mstart):
        self._mstart = _mstart
    
    @property
    def mmiddle(self):
        return self._mmiddle
    @mmiddle.setter
    def mmiddle(self, _mmiddle):
        self._mmiddle = _mmiddle

    @property
    def mend(self):
        return self._mend
    @mend.setter
    def mend(self, _mend):
        self._mend = _mend

    def M(self, _M):
        self._data.append(("M", _M))
        return self

    def m(self, _m):
        self._data.append(("m", _m))
        return self

    def l(self, _l):
        self._data.append(("l", _l))
        return self

    def __init__(self, begin, mstart=None, mmiddle=None, mend=None):
        super(Path, self).__init__()
        self._data = []; self._mstart = mstart;
        self._mmiddle = mmiddle; self._mend = mend
        self.M(begin)

    def marker_param(self):
        p = ''
        if self.mstart is not None:
            p += '''marker-start="url(#{marker})" '''.format(marker=self.mstart)
        if self.mmiddle is not None:
            p += '''marker-mid="url(#{marker})" '''.format(marker=self.mmiddle)
        if self.mend is not None:
            p += '''marker-end="url(#{marker})" '''.format(marker=self.mend)
        return p

    def draw(self, off, unit):
        orig = (off + self.orig) / unit
        path = ''
        for d in self.data:
            cmd, p = d; p = p / unit
            if cmd.isupper():
                p = p + orig
            path += "{} {} {}".format(cmd, p.x, p.y)
        print('''<path d="{}" stroke="black" stroke-width="1" {mp} />'''.format(path, mp=self.marker_param()))

# class Arrow(Path):
    

# ************************* Relate Modules ****************************

class Relate(Figure):
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

    @property
    def rule(self):
        return self._rule
    @rule.setter
    def rule(self, _rule):
        self._rule = _rule

    def __init__(self, ls, rule):
        super(Relate, self).__init__()
        self._ls = ls; self._rule = rule

    def draw(self, off, unit):
        global morph; l = len(self.ls) 
        for i in range(l-1):
            j = self.ls[i]; k = self.ls[i+1]
            F1 = morph[j]; F2 = morph[k]
            outp = F1.yieldout(); inp = F2.yieldin();
            self._rule(F1.orig + outp, F2.orig + inp).draw(off, unit)

    def __deepcopy__(self, memo):
        r = deepcopy(super(Relate, self), memo)
        r.__class__ = self.__class__
        r.ls = deepcopy(self.ls)
        r.d  = deepcopy(self.d)
        r.path = deepcopy(self.path)
        r.rule = deepcopy(self.rule)
        return r


class Connect(Relate):
    def __init__(self, ls, bm=None, em=None):
        rule = lambda b, e: Path(b, mstart=bm, mend=em).l(e - b)
        super(Connect, self).__init__(ls, rule)

# **********************************************************************

class Declare(Figure):
    @property
    def ls(self):
        return self._ls
    @ls.setter
    def ls(self, _ls):
        self._ls = _ls

    @property
    def d(self):
        return self._d
    @d.setter
    def d(self, _d):
        self._d = _d

    @property
    def rule(self):
        return self._rule
    @rule.setter
    def rule(self, _rule):
        self._rule = _rule

    def __init__(self, ls, rule):
        super(Declare, self).__init__()
        self._ls = ls; self._rule = rule
#        self._bewitch()
        self._align()

#    def _bewitch(self):
#        global morph; G = Ghost()
#        for i in self.ls:
#            if i not in morph:
#                G(i)

    def _align(self):
        global morph; l = len(self.ls); 
        coff = morph[self.ls[0]].orig
        for i, j in enumerate(self.ls):
            F = morph[j]
            if i != 0:
                F.orig = F.orig + coff
            # update coff
            coff = coff + self._rule(i, l)

    def draw(self, off, unit):
        global morph
        for j in self.ls:
            morph[j].draw(off, unit)

    def __deepcopy__(self, memo):
        r = deepcopy(super(Declare, self), memo)
        r.__class__ = self.__class__
        r.ls = deepcopy(self.ls)
        r.rule = deepcopy(self.rule)
        return r


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
    @property
    def fill(self):
        return self._fill
    @fill.setter
    def fill(self, _fill):
        self._fill = _fill

    def __init__(self, r, fill="none"):
        super(Circle, self).__init__(_vec=Vec(r, r)*2)
        self._fill = fill

    def draw(self, off, unit):
        orig = (off + self.orig) / unit; size = self.vec / unit; center = orig + size * (1/2)
        print('''<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="black" />'''.format(cx=center.x, cy=center.y, r=size.x / 2, fill=self.fill))

    def __deepcopy__(self, memo):
        r = deepcopy(super(Circle, self), memo)
        r.__class__ = self.__class__
        r.fill = self.fill
        return r

class Dot(Circle):
    def __init__(self, r):
        super(Dot, self).__init__(r, "black")

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

class Text(Figure):
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, text):
        self._text = text

    @property
    def ver(self):
        return self._ver
    @ver.setter
    def ver(self, ver):
        self._ver = ver

    @property
    def hor(self):
        return self._hor
    @hor.setter
    def hor(self, hor):
        self._hor = hor

    @property
    def fsize(self):
        return self._fsize
    @fsize.setter
    def fsize(self, fsize):
        self._fsize = fsize

    @property
    def ffam(self):
        return self._ffam
    @ffam.setter
    def ffam(self, ffam):
        self._ffam = ffam

    def __init__(self, text, fsize=1, ver=Ver.top, hor=Hor.left, ffam="Latin Modern Math"):
        super(Text, self).__init__()
        self._text = text; self._ver = ver; self._hor = hor;
        self._fsize = fsize; self._ffam = ffam;
        self.vec = Vec(0,0);

    def yieldmg(self):
        return Vec(0,0)

    def _convert(self, ver, hor):
        v, h = None, None
        if ver == Ver.top:
            v = "text-before-edge"
        elif ver == Ver.mid:
            v = "central"
        elif ver == Ver.bottom:
            v = "text-after-edge"
        
        if hor == Hor.left:
            h = "start"
        elif hor == Hor.mid:
            h = "middle"
        elif hor == Hor.right:
            h = "end"

        return v, h

    def draw(self, off, unit):
        orig = (off + self.orig) / unit; fsize = self.fsize * unit.y; v, h = self._convert(self.ver, self.hor)
        print('''<text x="{x}" y="{y}" font-family="{f}" font-size="{s}" fill="black" >'''.format(x=orig.x, y=orig.y, f=self.ffam, s=fsize))
        print('''\t<tspan text-anchor="{h}" dominant-baseline="{v}">{text}</tspan>'''.format(text=self.text, v=v, h=h))
        print('''</text>''')

    def __getitem__(self, p):
        raise ImplementationException("Text cannot deal with [] now")

    def __deepcopy__(self, memo):
        r = deepcopy(super(Text, self), memo)
        r.__class__ = self.__class__
        r.text = self.text;  r.fsize = self.fsize;
        r.ver = self.ver; r.hor = self.hor;
        r.ffam = self.ffam
        return r

def begin():
    print('''<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
    "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="{W_cm}cm" height="{H_cm}cm" viewBox="0 0 {W} {H}"
    xmlns="http://www.w3.org/2000/svg" version="1.1">
<title>a</title>'''.format(W_cm=MAX/100, H_cm=MAX/100, W=MAX, H=MAX))

def defs():
    print('''
<defs>
    <marker id="Triangle"
      viewBox="0 0 10 10" refX="10" refY="5" 
      markerUnits="strokeWidth"
      markerWidth="12" markerHeight="12"
      orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" />
    </marker>
    <marker id="Dot"
      viewBox="0 0 10 10" refX="5" refY="5" 
      markerUnits="strokeWidth"
      markerWidth="10" markerHeight="10"
      orient="auto">
      <circle cx="5" cy="5" r="4.5" fill="black" stroke="black" />
    </marker>
</defs>''')

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
    defs()
#    ************* f2 ************
#    inc = Circle(1)
#    for i in range(6):
#        inc = g(inc) if i % 2 == 1 else h(inc)
#    inc.draws()
#    *****************************

    ids    = list(range(8)) + [-1];
    primes = [2,3,5,7];
#    ids    = [0,1,203,3,4,5,6,7]
#    primes = [203,3,5,7];

    d = Declare(ids, lambda i, N: Vec.d(0) * 3 if i != 0 else Vec.d(0) * 2)
#    d = Declare(ids, lambda i, N: Vec.d(0) * sqrt(i+4))
    c1 = Connect(ids, bm="Dot", em="Triangle")
    c2 = Connect([0] + primes + [-1], bm="Dot", em="Triangle")

    a = Rect(1,1); a.o = [Vec(1/2,1/2)]
    aa = a[Vec(1/2,0)] + a[Vec(1/2,1)]
    aa.orig = Vec(0,0)

#    s = lambda text: Text(text, 3/4, Ver.mid, Hor.mid)
    s = lambda text: Text(text, (7/2-len(text)/2)/4, Ver.mid, Hor.mid)

    def r(text):
        b = Rect(1,2); b.i = [Vec(0,3/4), Vec(0,1/4)]
        return b[Vec(1/2,1/2)] + s(text)

    def np(text):
        b = Rect(1,1)[Vec(1/2,1/2)] + s(text)
        x = b[Vec(1,1/2)] + a[Vec(0,1/2)]; x.i = [Vec(0,1/2)]
        x.orig = Vec(0,1)
        return x
        
    def p(text):
        y = r(text)[Vec(1,1/2)] + aa[Vec(0,1/2)]
        return y

    for i in ids:
        t = str(i)
        if i == 0:
            aa(i); continue
        if i == -1:
            r("Nil")(i); continue
        if i in primes:
            p(t)(i)
        else:
            np(t)(i)

    d.draws();
    c1.draws();
    c2.draws();
    
    end()

sketch()
