set_lower = set("""\
abs
abs
acos
aimag
aint
alog
alog10
amax0
amax1
amin0
amin1
amod
anint
asin
atan
atan2
char
cmplx
cmplx
conjg
cos
cosh
dabs
dble
dcmplx
dconjg
dcos
dexp
dim
dimag
dlog
dlog10
dmax1
dmin1
dprod
dsin
dsign
dsqrt
exp
float
iabs
iand
ichar
idnint
index
int
ishft
len
len_trim
lge
lgt
lle
llt
log
log10
max
max0
max1
maxloc
min
min0
min1
mod
nint
real
real
sign
sin
sinh
sngl
sqrt
transfer
tan
tanh
""".splitlines())

extra_set_lower = set("""\
getenv
date
time
""".splitlines())
