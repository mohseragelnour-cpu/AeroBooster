import sys, math
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from modelB import *
INC = math.cos(math.radians(23.45))
V2 = dict(ins_mm=250.0, k_ins=0.0399, jacket=0.6, n_W=1.0)
sec("19. Which half of 'cap + secondary' carries the result? B 6 m2, v2 store build, solstice")
block("optical 0.58, loss x0.85 (as adopted row)", trough(6.0, eta0=0.58, a1=6.6*0.85, a2=0.016*0.85), inc=INC, **V2)
block("optical 0.55, loss x0.85 (cap helps heat only)", trough(6.0, eta0=0.55, a1=6.6*0.85, a2=0.016*0.85), inc=INC, **V2)
block("optical 0.54, loss x0.85 (cap shades 2 %)", trough(6.0, eta0=0.54, a1=6.6*0.85, a2=0.016*0.85), inc=INC, **V2)
block("optical 0.58, loss x1.00 (secondary helps light only)", trough(6.0, eta0=0.58), inc=INC, **V2)
block("optical 0.55, loss x1.00 (plain)", trough(6.0), inc=INC, **V2)
block("optical 0.55, loss x0.75", trough(6.0, eta0=0.55, a1=6.6*0.75, a2=0.016*0.75), inc=INC, **V2)
block("7 m2: optical 0.55, loss x1.00 (plain)", trough(7.0), inc=INC, **V2)
block("8 m2: optical 0.55, loss x1.00 (plain)", trough(8.0), inc=INC, **V2)
# first-principles receiver loss for comparison
sig=5.67e-8
for eps,lab in ((0.22,"black chrome"),(0.45,"selective paint"),(0.90,"black paint")):
    for Ta in (235,270,290):
        Tg = 60 + 0.18*(Ta-35)          # glass roughly 100 C at 270 C
        ee = 1/(1/eps + (21/32)*(1/0.88-1))
        rad = ee*sig*((Ta+273.15)**4-(Tg+273.15)**4)
        kair = 0.026+0.00007*((Ta+Tg)/2-25)
        cond = 2*math.pi*kair*(Ta-Tg)/math.log(32/21)/(math.pi*0.042)
        conv = cond*1.5
        mdl = 6.6*(Ta-35)+0.016*(Ta-35)**2
        print(f"  {lab:<16} absorber {Ta} C: radiation {rad:5.0f} + gap convection {conv:5.0f} = {rad+conv:5.0f} W/m2 absorber; model plain {mdl:5.0f}, x0.85 {mdl*0.85:5.0f}"
              + (f", black-paint model {6.6*(Ta-35)+0.067*(Ta-35)**2:5.0f}" if eps>0.8 else "") + (f", doubled {6.6*(Ta-35)+0.032*(Ta-35)**2:5.0f}" if 0.4<eps<0.5 else ""))
