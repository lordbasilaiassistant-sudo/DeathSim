"""
20-LINE VALIDATION TEST (anti-pattern #1: validate the core mechanism before building infra).

Question: does a single biophysical neuron with dynamic ion concentrations and an
O2/ATP-dependent Na/K pump (a) sit at a stable physiological rest, and (b) undergo
anoxic depolarization (the "wave of death") when the pump fails?

Model: Barreto & Cressman reduced single-cell model with [K]_o and [Na]_i dynamics.
Ref: Cressman, Ullah, Ziburkus, Schiff, Barreto (2009) J Comput Neurosci 26:159-170;
     Barreto & Cressman (2011) J Biol Phys 37:361-373.
"O2/ATP failure" is modeled as the pump strength rho -> 0 (the pump is ATP-powered).
If pump failure alone produces depolarization + [K]_o spike, the mechanism is validated.
"""
import numpy as np

# --- parameters (Cressman 2009) ---
C=1.0; phi=3.0
gNa=100.0; gNaL=0.0175; gK=40.0; gKL=0.05; gClL=0.05
Cl_i=6.0; Cl_o=130.0
gamma=0.044; beta=7.0; tau=1000.0
rho0=1.25; Gglia=66.0; eps=1.2; kbath=4.0

def rates(V):
    an=0.01*(V+34)/(1-np.exp(-(V+34)/10)); bn=0.125*np.exp(-(V+44)/80)
    am=0.1*(V+30)/(1-np.exp(-(V+30)/10));  bm=4*np.exp(-(V+55)/18)
    ah=0.07*np.exp(-(V+44)/20);            bh=1/(1+np.exp(-(V+14)/10))
    return an,bn,am,bm,ah,bh

Iapp=0.7  # tonic drive -> baseline firing (cortical neurons are active, not silent)

def step(s, ox, dt):
    # ox in [0,1] = oxygen/ATP availability. ALL active+vascular K clearance is
    # ATP/perfusion-dependent and fails together in cardiac arrest: neuronal pump,
    # glial pump, and vascular/diffusive washout.
    V,n,h,Ko,Nai = s
    Ki=140.0+(18.0-Nai); Nao=144.0-beta*(Nai-18.0)
    ENa=26.64*np.log(Nao/Nai); EK=26.64*np.log(Ko/Ki); ECl=26.64*np.log(Cl_i/Cl_o)
    an,bn,am,bm,ah,bh=rates(V); minf=am/(am+bm)
    INa=gNa*minf**3*h*(V-ENa)+gNaL*(V-ENa)
    IK =(gK*n**4+gKL)*(V-EK)
    ICl=gClL*(V-ECl)
    Ipump=ox*rho0/((1+np.exp((25-Nai)/3))*(1+np.exp(5.5-Ko)))
    Iglia=ox*Gglia/(1+np.exp((18-Ko)/2.5)); Idiff=ox*eps*(Ko-kbath)
    dV=(-INa-IK-ICl+Iapp)/C
    dn=phi*(an*(1-n)-bn*n); dh=phi*(ah*(1-h)-bh*h)
    dKo =(1/tau)*(gamma*beta*IK -2*beta*Ipump -Iglia -Idiff)
    dNai=(1/tau)*(-gamma*INa -3*Ipump)
    return np.array([V+dt*dV, n+dt*dn, h+dt*dh, Ko+dt*dKo, Nai+dt*dNai])

# --- run: 10 s healthy rest, then anoxia (ox -> 0) ---
dt=0.02; T=40000.0; nstep=int(T/dt)
s=np.array([-67.0,0.07,0.98,4.0,18.0])
out=np.zeros((nstep,5)); rho_off_t=10000.0
for i in range(nstep):
    t=i*dt
    ox = 1.0 if t < rho_off_t else 0.0       # cardiac arrest at t=10s: perfusion stops
    s=step(s, ox, dt); out[i]=s

t=np.arange(nstep)*dt/1000.0
# baseline window 5-10s, anoxic window 10-40s
base=(t>5)&(t<10); anox=(t>10)
print("BASELINE  V mean %.1f mV  Ko mean %.2f mM  Nai mean %.2f mM"%(out[base,0].mean(),out[base,3].mean(),out[base,4].mean()))
print("PEAK ANOX V max  %.1f mV  Ko max  %.2f mM  Nai max  %.2f mM"%(out[anox,0].max(),out[anox,3].max(),out[anox,4].max()))
print("FINAL     V       %.1f mV  Ko      %.2f mM  Nai      %.2f mM"%(out[-1,0],out[-1,3],out[-1,4]))
np.save("results/validate_trace.npy", np.column_stack([t,out]))
print("VALIDATION:", "PASS - anoxic depolarization (wave of death) reproduced"
      if (out[anox,0].max()>-40 and out[anox,3].max()>15) else "FAIL")
