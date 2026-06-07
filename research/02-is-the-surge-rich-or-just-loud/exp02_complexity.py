"""
EXPERIMENT 02 - Is the dying-brain gamma surge RICH (could support experience)
or just LOUD/SYNCHRONOUS (probably can't)?

Exp 01 showed energy failure reproduces the gamma surge. But a surge of POWER is
not a surge of EXPERIENCE. In living brains, the level of consciousness tracks
neural COMPLEXITY (Lempel-Ziv / PCI): high in wake/REM/psychedelics, LOW in
anesthesia, coma, and SEIZURE (hypersynchrony). A hypersynchronous gamma surge
could be seizure-like = the wrong kind of activity for rich experience.

Test: re-run the Exp-01 network recording per-neuron membrane V (250 Hz, 125 ch).
Compute multichannel Lempel-Ziv complexity (Schartner et al. 2015 method) and
synchrony in three windows: BASELINE (waking-like) vs SURGE vs SILENCE.

Prediction A ("vivid flash"): surge LZc >= baseline.
Prediction B ("loud but empty / seizure-like"): surge LZc < baseline despite higher power.

NOTE on interpretation: LZc is a CORRELATE of consciousness level, not a measure of
experience itself. This bounds the *capacity* of the activity to support rich
experience; it cannot prove presence or absence of feeling. Seam kept visible.

Refs: Schartner et al. 2015 PLoS ONE 10:e0133532 (LZc method); Casali et al. 2013
Sci Transl Med 5:198ra105 (PCI); Lempel & Ziv 1976 IEEE Trans Inf Theory.
"""
import numpy as np, argparse, gzip, json
from scipy.signal import hilbert
_ap=argparse.ArgumentParser(); _ap.add_argument("--seed",type=int,default=7); _A=_ap.parse_args()
rng=np.random.default_rng(_A.seed)

# ---------- Exp-01 model (frozen copy; same equations as ../01.../network.py) ----------
NE,NI=100,25; N=NE+NI; isE=np.zeros(N,bool); isE[:NE]=True; isI=~isE
C=1.0; phi=3.0
gNa=100.0;gNaL=0.0175;gK=40.0;gKL=0.05;gClL=0.05;Cl_i=6.0;Cl_o=130.0
gamma=0.044;beta=7.0;tau=1000.0;rho0=1.25;Gglia=66.0;eps=1.2;kbath=4.0
gEE,gEI,gIE,gII=0.10,0.20,0.40,0.10; tauE,tauI=2.0,8.0; VsynE,VsynI=0.0,-80.0; pcon=0.15
def conn(a,b,p): return (rng.random((a,b))<p).astype(float)
WEE=conn(NE,NE,pcon)*gEE; WIE=conn(NI,NE,pcon)*gEI
WEI=conn(NE,NI,pcon)*gIE; WII=conn(NI,NI,pcon)*gII
Iapp=2.2+0.3*rng.standard_normal(N)
def rates(V):
    an=0.01*(V+34)/(1-np.exp(-(V+34)/10)); bn=0.125*np.exp(-(V+44)/80)
    am=0.1*(V+30)/(1-np.exp(-(V+30)/10));  bm=4*np.exp(-(V+55)/18)
    ah=0.07*np.exp(-(V+44)/20);            bh=1/(1+np.exp(-(V+14)/10))
    return an,bn,am,bm,ah,bh
V=-67.0+np.zeros(N);n=0.07+np.zeros(N);h=0.98+np.zeros(N);Nai=18.0+np.zeros(N);Ko=4.0
gE=np.zeros(N);gI=np.zeros(N);spk_prev=np.zeros(N,bool)
dt=0.025;T=30000.0;arrest=10000.0;nstep=int(T/dt)
rec_every=int(4.0/dt); nrec=nstep//rec_every          # 250 Hz multichannel recording
Vchan=np.zeros((nrec,N)); pop=np.zeros(nrec); Ko_t=np.zeros(nrec); k=0
for i in range(nstep):
    t=i*dt; ox=1.0 if t<arrest else 0.0
    Ki=140.0+(18.0-Nai);Nao=144.0-beta*(Nai-18.0)
    ENa=26.64*np.log(Nao/Nai);EK=26.64*np.log(Ko/Ki);ECl=26.64*np.log(Cl_i/Cl_o)
    an,bn,am,bm,ah,bh=rates(V);minf=am/(am+bm)
    INa=gNa*minf**3*h*(V-ENa)+gNaL*(V-ENa); IK=(gK*n**4+gKL)*(V-EK); ICl=gClL*(V-ECl)
    Isyn=gE*(V-VsynE)+gI*(V-VsynI)
    Ipump=ox*rho0/((1+np.exp((25-Nai)/3))*(1+np.exp(5.5-Ko)))
    Iglia=ox*Gglia/(1+np.exp((18-Ko)/2.5));Idiff=ox*eps*(Ko-kbath)
    V=V+dt*((-INa-IK-ICl-Isyn+Iapp)/C)
    n=n+dt*phi*(an*(1-n)-bn*n);h=h+dt*phi*(ah*(1-h)-bh*h)
    Ko=Ko+dt*(1/tau)*(gamma*beta*IK.mean()-2*beta*Ipump.mean()-Iglia.mean()-Idiff)
    Nai=Nai+dt*(1/tau)*(-gamma*INa-3*Ipump)
    gE*=np.exp(-dt/tauE);gI*=np.exp(-dt/tauI)
    spk=(V>-20.0)&(~spk_prev)
    if spk.any():
        sE=spk&isE; sI=spk&isI
        if sE.any(): gE[:NE]+=WEE@sE[:NE]; gE[NE:]+=WIE@sE[:NE]
        if sI.any(): gI[:NE]+=WEI@sI[NE:]; gI[NE:]+=WII@sI[NE:]
    spk_prev=(V>-20.0)
    if i%rec_every==0 and k<nrec:
        Vchan[k]=V; pop[k]=spk.sum(); Ko_t[k]=Ko; k+=1
fs=250.0; tt=np.arange(nrec)/fs

# ---------- analysis ----------
def LZ76(s):
    s=list(s); n=len(s); i=k=l=0; i=0; k=1; l=1; c=1; kmax=1
    while True:
        if s[i+k-1]==s[l+k-1]:
            k+=1
            if l+k>n: c+=1; break
        else:
            if k>kmax: kmax=k
            i+=1
            if i==l:
                c+=1; l+=kmax
                if l+1>n: break
                i=0;k=1;kmax=1
            else: k=1
    return c

def binarize(X):
    B=np.zeros_like(X,dtype=int)
    for ch in range(X.shape[0]):
        x=X[ch]-X[ch].mean()
        if np.std(x)<1e-9: B[ch]=0; continue
        amp=np.abs(hilbert(x)); B[ch]=(amp>amp.mean()).astype(int)
    return B

def lzc_multichannel(X):
    # X: (channels, time). Two complexity measures, both normalized by a shuffled
    # surrogate (destroys structure). LOW value = ordered/uniform; HIGH = differentiated.
    B=binarize(X); seq=B.flatten().astype(np.uint8)
    sh=seq.copy(); rng.shuffle(sh)
    lz=LZ76(seq)/LZ76(sh)                                   # normalized Lempel-Ziv (LZ76)
    gz=len(gzip.compress(seq.tobytes(),9))/len(gzip.compress(sh.tobytes(),9))  # gzip/LZ77 cross-check
    return lz, gz, B.mean()

def synchrony(X):
    # 1 - (mean of per-channel variance)/(variance of mean field): high = synchronous
    mf=X.mean(0)
    num=mf.var(); den=X.var(1).mean()
    return num/ (den+1e-12)

def power(X): return X.var(1).mean()

# EQUAL-LENGTH windows (LZ complexity scales with length -> fair comparison requires it)
L=1.5  # seconds per window = 375 samples at 250 Hz
def winc(c): m=(tt>=c-L/2)&(tt<c+L/2); return Vchan[m].T  # centered window -> (channels, time)
rp=np.convolve(pop,np.ones(20)/20,'same'); pidx=np.where(tt>=arrest/1000)[0]
pkt=tt[pidx[rp[pidx].argmax()]]
W={"baseline":winc(7.0),"surge":winc(pkt),"silence":winc(T/1000-L/2-0.05)}
nmin=min(X.shape[1] for X in W.values()); W={k:X[:,:nmin] for k,X in W.items()}  # exact equal length
print(f"[seed {_A.seed}] surge peak @ t={pkt:.2f}s (+{pkt-arrest/1000:.2f}s); window={nmin} samples each")
res={}
for name,X in W.items():
    lz,gz,act=lzc_multichannel(X); sy=synchrony(X); pw=power(X)
    res[name]=dict(LZc=round(float(lz),3),gzipC=round(float(gz),3),synchrony=round(float(sy),2),
                   power=round(float(pw),1),active_frac=round(float(act),3))
    print(f"  {name:9s} LZc={res[name]['LZc']:.3f} gzipC={res[name]['gzipC']:.3f} "
          f"synchrony={res[name]['synchrony']:6.2f} power={res[name]['power']:7.1f}")
np.savez(f"results/exp02_seed{_A.seed}.npz",tt=tt,pop=pop,Ko=Ko_t,Vchan=Vchan,pkt=pkt,arrest=arrest/1000)
b,s=res["baseline"]["LZc"],res["surge"]["LZc"]
verdict=("A_richer" if s>b*1.05 else "B_loud_not_rich" if s<b*0.95 else "ambiguous")
rec={"seed":_A.seed,"verdict":verdict,"surge_over_baseline_LZc":round(s/b,2),
     "baseline":res["baseline"],"surge":res["surge"],"silence":res["silence"]}
with open("results/exp02_summary.jsonl","a") as fh: fh.write(json.dumps(rec)+"\n")
print(f"  VERDICT[{_A.seed}]: {verdict}  surge/baseline LZc={s/b:.2f} "
      f"(surge synchrony {res['surge']['synchrony']} vs {res['baseline']['synchrony']}, "
      f"power {res['surge']['power']} vs {res['baseline']['power']})")
