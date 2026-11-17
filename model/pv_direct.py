"""PV string driving a fixed resistor directly vs an MPPT, clear-sky day, hot climate.
Module (typical 72-cell 450 W): Isc 11.6 A, Voc 49.5 V, Imp 11.0 A, Vmp 41.0 V at STC.
Explicit single-diode approximation; Voc -0.28 %/K, Isc +0.05 %/K, cell T = Tamb + 0.03*G."""
import math
Isc0,Voc0,Imp0,Vmp0=11.6,49.5,11.0,41.0
C2=(Vmp0/Voc0-1)/math.log(1-Imp0/Isc0); C1=(1-Imp0/Isc0)*math.exp(-Vmp0/(C2*Voc0))
def I(V,G,Tc,ns):
    isc=Isc0*G/1000*(1+0.0005*(Tc-25)); voc=Voc0*(1-0.0028*(Tc-25))*(1+0.06*math.log(max(G,1)/1000)) if G>1 else 0
    v=V/ns
    if voc<=0 or v>=voc: return 0.0
    i=isc*(1-C1*(math.exp(v/(C2*voc))-1)); return max(i,0.0)
def op_point(R,G,Tc,ns):  # solve V = I(V)*R
    lo,hi=0.0,Voc0*ns*1.1
    for _ in range(60):
        V=(lo+hi)/2
        if I(V,G,Tc,ns)*R>V: lo=V
        else: hi=V
    V=(lo+hi)/2; return V*I(V,G,Tc,ns)
def mpp(G,Tc,ns): return max(V*I(V,G,Tc,ns) for V in [ns*0.25*k for k in range(int(Voc0*4)+1)])
def day(ns,R,Tamb=38):
    Ed=Em=0
    for m in range(6*60,18*60+1,5):
        G=1000*max(0,math.sin(math.pi*(m-360)/720))**1.15*0.95
        Tc=Tamb+0.03*G
        Ed+=op_point(R,G,Tc,ns)*5/60; Em+=mpp(G,Tc,ns)*5/60
    return Ed/1000,Em/1000
for ns in (2,3):
    best=max(((day(ns,R/2)[0],R/2) for R in range(4,40)),key=lambda t:t[0])
    Ed,Em=day(ns,best[1]); print(f"{ns} panels in series: MPPT {Em:.2f} kWh/day; best fixed R {best[1]:.1f} ohm -> {Ed:.2f} kWh/day ({100*Ed/Em:.0f}% of MPPT)")
    for R in (best[1]*0.7,best[1]*1.4, 52.9):
        Ed,_=day(ns,R); print(f"   R {R:5.1f} ohm -> {Ed:.2f} kWh/day ({100*Ed/Em:.0f}%)")
