"""
EXPERIMENT 01 - Does energy failure alone produce the end-of-life gamma surge?

A biophysical E/I network of Cressman-type neurons (dynamic [Na]_i per cell, a shared
extracellular [K]_o compartment, conductance-based synapses). At t = t_arrest, oxygen/
perfusion is withdrawn (ox: 1 -> 0): the ATP-dependent Na/K pumps and vascular K+
clearance fail. NOTHING about consciousness is in the model - only ion biophysics.

Hypothesis H: the surge of synchronized high-frequency (gamma) population activity
reported in dying brains (Borjigin 2013 rat; 2023 human) is a GENERIC dynamical
consequence of energy failure, not evidence of a special end-of-life process.

Prediction if H holds: after arrest, the population shows a TRANSIENT burst of
high-frequency, more-synchronized activity (a gamma-power surge) that PRECEDES
isoelectric silence (depolarization block) - the exact order Borjigin reports.

Refs: Cressman et al. 2009 J Comput Neurosci 26:159; Barreto & Cressman 2011;
      Borjigin et al. 2013 PNAS 110:14432; Wei, Ullah, Schiff 2014 J Neurosci.

Usage:  py network.py [--seed N] [--temp C] [--out TAG]
"""
import numpy as np, argparse, json, os

ap=argparse.ArgumentParser()
ap.add_argument("--seed",type=int,default=1)
ap.add_argument("--temp",type=float,default=37.0)  # brain temperature (deg C)
ap.add_argument("--out",type=str,default="base")
ap.add_argument("--drive",type=float,default=2.2)  # tonic drive -> waking-like baseline firing
ap.add_argument("--T",type=float,default=30000.0)  # ms
ap.add_argument("--arrest",type=float,default=10000.0)
a=ap.parse_args(); rng=np.random.default_rng(a.seed)

# ---- network size ----
NE,NI=100,25; N=NE+NI
isE=np.zeros(N,bool); isE[:NE]=True; isI=~isE

# ---- single-cell params (Cressman 2009) ----
C=1.0
# temperature: gating speed and pump rate scale with Q10. 37C is reference.
phi=3.0*1.3**((a.temp-37.0)/10.0)          # gating Q10 ~1.3
pumpQ10=1.0                                 # pump scaling handled in 'ox' baseline below
gNa=100.0; gNaL=0.0175; gK=40.0; gKL=0.05; gClL=0.05
Cl_i=6.0; Cl_o=130.0
gamma=0.044; beta=7.0; tau=1000.0
rho0=1.25; Gglia=66.0; eps=1.2; kbath=4.0

# ---- synapses (conductance-based; PING gamma) ----
gEE,gEI,gIE,gII=0.10,0.20,0.40,0.10        # peak conductances
tauE,tauI=2.0,8.0                          # ms decay (AMPA-like, GABA-like)
VsynE,VsynI=0.0,-80.0
pcon=0.15                                   # connection prob
# connectivity masks (post x pre)
def conn(npost,npre,p): return (rng.random((npost,npre))<p).astype(float)
WEE=conn(NE,NE,pcon)*gEE; WIE=conn(NI,NE,pcon)*gEI   # E->E, E->I
WEI=conn(NE,NI,pcon)*gIE; WII=conn(NI,NI,pcon)*gII   # I->E, I->I
Iapp=a.drive+0.3*rng.standard_normal(N)      # heterogeneous tonic drive (waking-like baseline)

def rates(V):
    an=0.01*(V+34)/(1-np.exp(-(V+34)/10)); bn=0.125*np.exp(-(V+44)/80)
    am=0.1*(V+30)/(1-np.exp(-(V+30)/10));  bm=4*np.exp(-(V+55)/18)
    ah=0.07*np.exp(-(V+44)/20);            bh=1/(1+np.exp(-(V+14)/10))
    return an,bn,am,bm,ah,bh

# ---- state ----
V=-67.0+np.zeros(N); n=0.07+np.zeros(N); h=0.98+np.zeros(N); Nai=18.0+np.zeros(N)
Ko=4.0                                       # shared extracellular K+ (well-mixed local ECS)
sE=np.zeros(N); sI=np.zeros(N)               # synaptic gates per neuron (its own outgoing spike state)
gE=np.zeros(N); gI=np.zeros(N)               # received conductances per post neuron

dt=0.025; nstep=int(a.T/dt)
rec_dt=1.0; rec_every=int(rec_dt/dt)         # record pop rate at 1 kHz
nrec=nstep//rec_every
pop=np.zeros(nrec); Ko_t=np.zeros(nrec); V_t=np.zeros(nrec); sync_t=np.zeros(nrec)
spk_prev=np.zeros(N,bool); k=0; spkcount=0

for i in range(nstep):
    t=i*dt
    ox=1.0 if t<a.arrest else 0.0
    Ki=140.0+(18.0-Nai); Nao=144.0-beta*(Nai-18.0)
    ENa=26.64*np.log(Nao/Nai); EK=26.64*np.log(Ko/Ki); ECl=26.64*np.log(Cl_i/Cl_o)
    an,bn,am,bm,ah,bh=rates(V); minf=am/(am+bm)
    INa=gNa*minf**3*h*(V-ENa)+gNaL*(V-ENa)
    IK =(gK*n**4+gKL)*(V-EK)
    ICl=gClL*(V-ECl)
    Isyn=gE*(V-VsynE)+gI*(V-VsynI)
    Ipump=ox*rho0/((1+np.exp((25-Nai)/3))*(1+np.exp(5.5-Ko)))
    Iglia=ox*Gglia/(1+np.exp((18-Ko)/2.5)); Idiff=ox*eps*(Ko-kbath)
    dV=(-INa-IK-ICl-Isyn+Iapp)/C
    V=V+dt*dV
    n=n+dt*phi*(an*(1-n)-bn*n); h=h+dt*phi*(ah*(1-h)-bh*h)
    # shared Ko driven by MEAN neuronal K efflux (population ECS)
    meanIK=IK.mean(); meanIpump=Ipump.mean()
    Ko=Ko+dt*(1/tau)*(gamma*beta*meanIK -2*beta*meanIpump -Iglia.mean() -Idiff)
    Nai=Nai+dt*(1/tau)*(-gamma*INa -3*Ipump)
    # synaptic conductances decay; spikes (upward threshold cross at -20mV) add to post
    gE*=np.exp(-dt/tauE); gI*=np.exp(-dt/tauI)
    spk=(V> -20.0)&(~spk_prev)
    if spk.any():
        spkE=spk&isE; spkI=spk&isI
        if spkE.any():
            gE[:NE]+=WEE@spkE[:NE]; gE[NE:]+=WIE@spkE[:NE]
        if spkI.any():
            gI[:NE]+=WEI@spkI[NE:]; gI[NE:]+=WII@spkI[NE:]
    spk_prev=(V>-20.0)
    spkcount+=int(spk.sum())
    if i%rec_every==0 and k<nrec:
        pop[k]=spk.sum(); Ko_t[k]=Ko; V_t[k]=V.mean(); sync_t[k]=V.std(); k+=1

np.savez(f"results/net_{a.out}.npz", pop=pop, Ko=Ko_t, Vmean=V_t, Vstd=sync_t,
         rec_dt=rec_dt, arrest=a.arrest, temp=a.temp, seed=a.seed, T=a.T)
# quick console summary
fs=1000.0/rec_dt
def bandpow(x, lo, hi):
    x=x-x.mean(); f=np.fft.rfftfreq(len(x),1/fs); P=np.abs(np.fft.rfft(x))**2
    return P[(f>=lo)&(f<hi)].sum()
base=slice(int(5000/rec_dt),int(a.arrest/rec_dt))
post=slice(int(a.arrest/rec_dt),int((a.arrest+8000)/rec_dt))
gbase=bandpow(pop[base],25,100); gpost=bandpow(pop[post],25,100)
# surge & silence timing (1 kHz rate signal)
tt=np.arange(len(pop))*rec_dt/1000.0; tA=a.arrest/1000.0
r=np.convolve(pop,np.ones(20)/20,'same')
pidx=np.where(tt>=tA)[0]; pk=r[pidx].max(); pkt=tt[pidx[r[pidx].argmax()]]
below=pidx[(r[pidx]<0.05*pk)&(tt[pidx]>pkt)]
silence=float(tt[below[0]]) if len(below) else float('nan')
surge_precedes_silence = (not np.isnan(silence)) and (pkt < silence)
rec={"out":a.out,"seed":a.seed,"temp":a.temp,"drive":a.drive,"spikes":spkcount,
     "gamma_base":round(gbase,2),"gamma_post":round(gpost,2),
     "gamma_ratio":round(gpost/max(gbase,1e-9),2),"Ko_peak":round(float(Ko_t.max()),1),
     "Vmean_final":round(float(V_t[-1]),1),"surge_t":round(float(pkt-tA),2),
     "silence_t":round(silence-tA,2) if not np.isnan(silence) else None,
     "surge_precedes_silence":bool(surge_precedes_silence)}
with open("results/summary.jsonl","a") as fh: fh.write(json.dumps(rec)+"\n")
print(f"[{a.out} seed{a.seed} {a.temp}C] spikes={spkcount} gamma_ratio(post/base)={rec['gamma_ratio']} "
      f"Ko_peak={rec['Ko_peak']} surge@+{rec['surge_t']}s silence@+{rec['silence_t']}s "
      f"precedes={rec['surge_precedes_silence']}")
