import math
from geo import *
i1 = i1_polys(); i2 = i2_polys()
dec = lambda P,k: P[::k]
I2 = [dec(i2['rim'],2), i2['islet'], i2['bridge']]
I1 = [i1['rim'], i1['islet'], i1['bridge']]
LP = [LOBBY['picos']]
out=[]
for yaw in range(84, 113, 2):
  for R in (160.0, 220.0):
    for s in range(60, 241, 20):
      F = Fit(yaw, R, float(s), 120.0); P = F.polys()
      me=[P['rim'], P['summon'], P['exit_bridge'], P['islet']]
      g2 = multi_dist(me, I2); gl = multi_dist(me+[P['arrival']], LP); g1 = multi_dist(me, I1)
      out.append((min(g2, gl), round(F.length), yaw, R, s, round(g2), round(gl), round(g1)))
out.sort(reverse=True)
for o in out[:15]: print(o)
print('---- best per length bucket')
for Lmax in (200, 230, 260, 290, 320):
  c=[o for o in out if o[1]<=Lmax]
  if c: print(Lmax, max(c))
