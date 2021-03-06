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

    def __truediv__(self, c):
        d = self._c / c; return Vec(d.real, d.imag)

    def muleach(self, v):
        '''(x,y) = (a,b)/(c,d)でuとvの座標積: (x,y) = (a*c, b*d)'''
        return Vec(self.x * v.x, self.y * v.y)

    def diveach(self, v):
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

class Param:
    def __init__(self, **kwargs):
        self._param = kwargs
    
    def encode(self):
        s = ''
        for k in self._param:
            s += '''{}="{}" '''.format(k, self._param[k])
        return s

    def get(self, key):
        return self._param[key]

    def add(self, key, value):
        self._param[key] = value
        return self

    def remove(self, key):
        del self._param[key]
        return self

    def __deepcopy__(self, memo):
        return Param(**deepcopy(self._param, memo))

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

    @property
    def rot(self):
        return self._rot
    @rot.setter
    def rot(self, _rot):
        self._rot = _rot

    @property
    def param(self):
        return self._param
    @param.setter
    def param(self, _param):
        self._param = _param

    @property
    def fill(self):
        return self.param.get('fill')
    @fill.setter
    def fill(self, _fill):
        self.param.add('fill', _fill)

    @property
    def stroke(self):
        return self.param.get('stroke')
    @stroke.setter
    def stroke(self, _stroke):
        self.param.add('stroke', _stroke)

    @property
    def stroke_width(self):
        return self.param.get('stroke-width')
    @stroke_width.setter
    def stroke_width(self, _stroke_width):
        self.param.add('stroke-width', _stroke_width)

    @property
    def opacity(self):
        return self.param.get('opacity')
    @opacity.setter
    def opacity(self, _opacity):
        self.param.add('opacity', _opacity)
    '''*************************************************'''

    '''initializer'''
    def __init__(self, _i=[], _o=[], _mg=[], _orig=Vec(0,0), _vec=Vec(1,1), _ch=[], _param=Param()):
        self._i    = _i
        self._o    = _o
        self._mg   = _mg
        self._orig  = _orig
        self._vec    = _vec
        self._ch   = _ch
        self._p = None
        self._rot = 0
        self._param = _param

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
        print('''<g transform="rotate({.rot})">'''.format(self))
        self.draw(off + self.calcoff(), unit)
        print('''</g>''')

    def draw(self, off, unit):
        for f in self.ch:
            print('''<g transform="rotate({.rot})">'''.format(self))
            f.draw(off + self.orig, unit)
            print('''</g>''')

    '''***************** helper funcs *****************'''
    def orig_to_ac(self):
        if self.p is not None:
            tmp = self.orig + self.p.orig_to_ac()
            return tmp
        return Vec(0, 0)
#        return self.orig

    def rrc_to_ac(self, p):
        return self.orig_to_ac() + p.muleach(self.vec)

    def ac_to_rrc(self, p):
        return (p - self.orig_to_ac()).diveach(self.vec)

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
            tmp = self.i[0].muleach(self.vec); self.i = self.i[1:]
            return tmp
        for c in self.ch:
            t = c.yieldin()
            if t is not None:
                return t + c.orig
    
    def yieldout(self):
        if self.o:
            tmp = self.o[0].muleach(self.vec); self.o = self.o[1:]
            return tmp
        for c in self.ch:
            t = c.yieldout()
            if t is not None:
                return t + c.orig

    def yieldmg(self):
        if self.mg:
            tmp = self.mg[0].muleach(self.vec); self.mg = self.mg[1:]
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
        f.rot = deepcopy(self.rot, memo)
        f.param = deepcopy(self.param, memo)
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

    def hide(self):
        f = deepcopy(self); f.opacity = 0; return f

class Ghost(Figure):
    def __init__(self):
        super(Ghost, self).__init__()
        self.c = Circle(1/2)

    def yieldin(self):
        return Vec(1/2,1/2).muleach(self.c.vec)

    def yieldout(self):
        return Vec(1/2,1/2).muleach(self.c.vec)

    def yieldmg(self):
        return Vec(1/2,1/2).muleach(self.c.vec)
    
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

    def Q(self, _C, _E):
        self._data.append(("Q", _C))
        self._data.append((None, _E))
        return self

    def q(self, _c, _e):
        self._data.append(("q", _c))
        self._data.append((None, _e))
        return self

    def z(self):
        self._data.append(('z', None))

    def __init__(self, begin, mstart=None, mend=None, mmiddle=None, fill="none", stroke="black", stroke_width="1"):
        super(Path, self).__init__()
        self._data = []; self._mstart = mstart;
        self._mmiddle = mmiddle; self._mend = mend
        self.fill = fill; self.stroke = stroke; self.stroke_width = stroke_width;
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
        orig = (off + self.orig).muleach(unit)
        path = ''
        for d in self.data:
            cmd, p = d;
            if cmd is None:
                cmd = ""
            if p is None:
                path += cmd
            p = p.muleach(unit)
            if cmd.isupper():
                p = p + orig
            path += "{} {} {}".format(cmd, p.x, p.y)
        print('''<path d="{}" {p} {mp} />'''.format(path, p=self.param.encode(), mp=self.marker_param()))

# class Arrow(Path):
class Straight(Path):
    def __init__(self, b, e, bm=None, em=None):
        super(Straight, self).__init__(b, bm, em)
        self.l(e - b)

class Bez2(Path):
    def __init__(self, b, c, e, bm=None, em=None):
        super(Bez2, self).__init__(b, bm, em)
        self.Q(c, e)
    
class Curve(Bez2):
    def mtoc(self, b, m, e):
        return m * 2 - (b + e) / 2

    def __init__(self, b, m, e, bm=None, em=None):
        super(Curve, self).__init__(b, self.mtoc(b, m, e), e, bm, em)

# ************************* Relate Modules ****************************

class Pattern(Figure):
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
        super(Pattern, self).__init__()
        self._ls = ls; self._rule = rule

    def draw(self, off, unit):
        global morph; l = len(self.ls) 
        for i in range(l-1):
            j = self.ls[i]; k = self.ls[i+1]
            F1 = morph[j]; F2 = morph[k]
            outp = F1.yieldout(); inp = F2.yieldin();
            self._rule(i)(F1.orig + outp, F2.orig + inp).draw(off, unit)

    def __deepcopy__(self, memo):
        r = deepcopy(super(Pattern, self), memo)
        r.__class__ = self.__class__
        r.ls = deepcopy(self.ls)
        r.d  = deepcopy(self.d)
        r.path = deepcopy(self.path)
        r.rule = deepcopy(self.rule)
        return r

class Relate(Pattern):
    def __init__(self, ls, rule):
        super(Relate, self).__init__(ls, lambda i: rule)

class Connect(Relate):
    def __init__(self, ls, bm=None, em=None):
        rule = lambda b, e: Straight(b, e)
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
    def __init__(self, w, h, fill="none", stroke="black"):
        super(Rect, self).__init__(_vec=Vec(w, h))
        self.fill = fill; self.stroke = stroke

    def draw(self, off, unit):
        orig = (off + self.orig).muleach(unit); size = self.vec.muleach(unit)
        print('''<rect x="{x}" y="{y}" width="{w}" height="{h}" {p} />'''.format(x=orig.x, y=orig.y, w=size.x, h=size.y, p=self.param.encode()))

    def rotate(self, theta):
        c = deepcopy(self)
        ctr = Vec(1/2,1/2);
        for k,i in enumerate(c.i):
            c.i[k] = (i - ctr).rot(theta) + ctr
        for k,o in enumerate(c.o):
            c.o[k] = (o - ctr).rot(theta) + ctr
        for k,mg in enumerate(c.mg):
            c.mg[k] = (mg - ctr).rot(theta) + ctr
        return c

    def __deepcopy__(self, memo):
        r = deepcopy(super(Rect, self), memo)
        r.__class__ = self.__class__
        return r

class Circle(Figure):
    @property
    def r(self):
        return self.vec.x / 2
    @property
    def center(self):
        return Vec(1/2, 1/2)
    
    def __init__(self, r, fill="none", stroke="black"):
        super(Circle, self).__init__(_vec=Vec(r, r)*2)
        self.fill = fill; self.stroke = stroke

    def draw(self, off, unit):
        orig = (off + self.orig).muleach(unit); size = self.vec.muleach(unit); center = orig + size / 2
        print('''<circle cx="{cx}" cy="{cy}" r="{r}" {p} />'''.format(cx=center.x, cy=center.y, r=size.x / 2, p=self.param.encode()))

    def rotate(self, theta):
        c = deepcopy(self)
        ctr = self.center;
        for k,i in enumerate(c.i):
            c.i[k] = (i - ctr).rot(theta) + ctr
        for k,o in enumerate(c.o):
            c.o[k] = (o - ctr).rot(theta) + ctr
        for k,mg in enumerate(c.mg):
            c.mg[k] = (mg - ctr).rot(theta) + ctr
        return c

    def __deepcopy__(self, memo):
        r = deepcopy(super(Circle, self), memo)
        r.__class__ = self.__class__
        return r

class Dot(Circle):
    def __init__(self, r, fill="black"):
        super(Dot, self).__init__(r, fill=fill)

class Line(Figure):
    @property
    def l(self):
        return self.vec.r()

    def __init__(self, x, y=0, stroke_width="1"):
        super(Line, self).__init__(_vec=Vec(x, y))
        self.stroke_width = stroke_width

    def draw(self, off, unit):
        orig = (off + self.orig).muleach(unit); end = orig + self.vec.muleach(unit)
        print('''<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {p} />'''.format(x1=orig.x, y1=orig.y, x2=end.x, y2=end.y, p=self.param.encode()))

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
        orig = (off + self.orig).muleach(unit); fsize = self.fsize * unit.y; v, h = self._convert(self.ver, self.hor)
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

def morphscript(f):
    def wrapper(*args, **kwargs):
        begin()
        defs()
        f(*args, **kwargs)
        end()
    return wrapper

def sketch():
    begin()
    defs()

    ids = [1,2,3]
    d = Declare(ids, lambda i, N: (Vec.d(240) + Vec.d(120 * i)) * 4)

    def arrow(b, e):
        mid = (b + e) / 2
        up  = (e - b).rot(90) * 0.15
        return Curve(b, mid + up, e, em="Triangle")

    r1 = Relate([1,2,3,1], arrow)
    r2 = Relate([3,2,1,3], arrow)

    c = Circle(1); c.orig = Vec(10,10)
    c.i = [Vec(1/2,1/2), Vec(1/2,1/2), Vec(1/2,1/2)]
    c.o = [Vec(1/2,1/2), Vec(1/2,1/2), Vec(1/2,1/2)]

    for i in ids:
        c(i)
    
    d.draws()
    r1.draws()
    r2.draws()
    end()

def test2():
    begin()
    defs()

    ids = [1,2,3]
    d = Declare(ids, lambda i, N: (Vec.d(240) + Vec.d(120 * i)) * 4)

    def arrow(b, e):
        mid = (b + e) / 2
        up  = (e - b).rot(90) * 0.15
        return Curve(b, mid + up, e, em="Triangle")

    r1 = Relate([1,2,3,1], arrow);
    r2 = Relate([3,2,1,3], arrow);
    
    def node():
        c = Circle(2/3); c.orig = Vec(10,10)
        def d(theta):
            return Vec(1/2,1/2) + Vec.d(theta) / 2
        c.i = [d(-140), d(-70)]; c.o = [d(-40), d(-110)]
        return c

    for i in ids:
        node().rotate(240*(i-1))(i)

    d.draws()
    r1.draws()
    r2.draws()


    end()

@morphscript
def rott(n):
    ids = list(range(n))
    d = Declare(ids, lambda i, N: Vec.d(180+180/N + 360/N *i) * 4)
    #d = Declare(ids, lambda i, N: Vec.d(180+360/N + 360/N *i) * 4)

    def arrow(b, e):
        mid = (b + e) / 2
        up  = (e - b).rot(-90) * 0.15
        return Curve(b, mid + up, e, em="Triangle")

    r1 = Relate(ids + [0], arrow);
    r2 = Relate(list(reversed(ids)) + [n-1], arrow);

    def node():
        c = Circle(2/3); c.orig = Vec(10,10)
        def d(theta):
            return Vec(1/2,1/2) + Vec.d(theta) / 2
        mart = 15
        c.i = [d(-180/n + mart), d(180+180/n + mart)]
        c.o = [d(180+180/n - mart), d(-180/n - mart)]
#        c.o = list(reversed([d(-180/n + mart), d(180+180/n + mart)]))
#        c.i = list(reversed([d(180+180/n - mart), d(-180/n - mart)]))
        return c

    for i in ids:
        node().rotate(360/n * i)(i)
        #node().rotate(180/n + 360/n * i)(i)

    d.draws()
    r1.draws()
    r2.draws()

@morphscript
def comp_easy(n):
    ids = list(range(n))
    d = Declare(ids, lambda i, N: Vec.d(180+180/N + 360/N *i) * 4)

    def node(i):
        c = Circle(1/3, fill="red"); c.orig = Vec(10,10)
        def d(theta):
            return Vec(1/2,1/2) + Vec.d(theta) / 2
        mart = 15

        m = n - 1
        def angle(k):
            return -90 - mart*(m-1)/2 + mart*k

        c.i = [d(-90)] * m
        c.o = [d(-90)] * m

        return c.rotate(360/n * i)
    
    for i in ids:
        node(i)(i)

    for i in ids:
        for j in range(i+1, n):
            Connect([i,j]).draws()
            # Connect([i,j],em="Triangle").draws()
    d.draws()


@morphscript
def comp(n):
    ids = list(range(n))
    d = Declare(ids, lambda i, N: Vec.d(180+180/N + 360/N *i) * 4)

    def node(i):
        c = Circle(1/3, fill="red"); c.orig = Vec(15,10)
        def d(theta):
            return Vec(1/2,1/2) + Vec.d(theta) / 2
        mart = 15
        # mart = lambda k: 15 * (1 - 1 / sqrt(k))

        m = n - 1
        def angle(k):
            return -90 - mart*(m-1)/2 + mart*k

        c.i = [d(angle(k)) for k in range(m-i,m)]
        c.o = [d(angle(k)) for k in range(m-i)]

        return c.rotate(360/n * i)
    
    for i in ids:
        node(i)(i)

#    for i in ids:
#        for j in ids:
#            if i != j:
#                Connect([i,j]).draws();

#    for i in ids:
#        for j in range(i+1, i+n):
#            Connect([i,j % n]).draws()

    for i in ids:
        for j in range(i+1, n):
            Connect([i,j]).draws()
            # Connect([i,j],em="Triangle").draws()
    d.draws()

@morphscript
def comp_partial(n):
    ids = list(range(n))
    d = Declare(ids, lambda i, N: Vec.d(180+180/N + 360/N *i) * 4)

    def node(i):
        c = Circle(1/3, fill="red"); c.orig = Vec(10,10)
        def d(theta):
            return Vec(1/2,1/2) + Vec.d(theta) / 2
        mart = 15
        # mart = lambda k: 15 * (1 - 1 / sqrt(k))

        m = n - 1
        def angle(k):
            return -90 - mart*(m-1)/2 + mart*k

        c.i = [d(angle(k)) for k in range(m-i,m)]
        c.o = [d(angle(k)) for k in range(m-i)]

        return c.rotate(360/n * i)
    
    for i in ids:
        node(i)(i)

    def line(b, e, vanish=False):
        s = Straight(b, e)
        return s.hide() if vanish else s

    for i in ids:
        for j in range(i+1, n):
            if j == i + 1 or (i == 0 and j == n-1):
                Relate([i,j], lambda b,e: line(b,e,True)).draws()
            else:
                Relate([i,j], lambda b,e: line(b,e,False)).draws()
            # Connect([i,j]).draws()
            # Pattern([i,j], lambda i: (lambda b,e: line(b,e,True)) if i % 2 == 0 else (lambda b,e: line(b,e,False)) ).draws()
                
    d.draws()


#sketch()
#test2()
rott(5)
#comp_easy(4)
#comp(4)
#comp_partial(12)
