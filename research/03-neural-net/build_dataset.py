"""
STEP ZERO for the classifier: sweep the biophysical simulator into a labeled dataset.

Vary drive x connectivity-seed (the simulator IS the data generator). For each run,
record per-neuron V (125 ch @ 250 Hz), detect the surge, slice short windows, and
label each by regime {0 baseline / 1 surge / 2 silence}. Save one dataset.npz with
X (windows), y (labels), and run_id (for GROUPED train/test splits so we never test
on a window from a network we trained on).

Output: results/dataset.npz  with X float16 (N,125,WIN), y int8 (N,), run_id int16 (N,)
Usage: py build_dataset.py
"""
import numpy as np, itertools, os
WIN=48; STRIDE=10; FS=250.0
DRIVES=[1.8,2.2,2.6]; SEEDS=[1,2,3,4,5,6]          # 18 runs
os.makedirs("results",exist_ok=True)

# ---- model (frozen copy of Exp-01/02 network) ----
def simulate(drive, seed):
    rng=np.random.default_rng(seed)
    NE,NI=100,25; N=NE+NI; isE=np.zeros(N,bool); isE[:NE]=True; isI=~isE
    C=1.0;phi=3.0;gNa=100.0;gNaL=0.0175;gK=40.0;gKL=0.05;gClL=0.05;Cl_i=6.0;Cl_o=130.0
    gamma=0.044;beta=7.0;tau=1000.0;rho0=1.25;Gglia=66.0;eps=1.2;kbath=4.0
    gEE,gEI,gIE,gII=0.10,0.20,0.40,0.10;tauE,tauI=2.0,8.0;VsynE,VsynI=0.0,-80.0;pcon=0.15
    def conn(a,b,p): return (rng.random((a,b))<p).astype(float)
    WEE=conn(NE,NE,pcon)*gEE;WIE=conn(NI,NE,pcon)*gEI
    WEI=conn(NE,NI,pcon)*gIE;WII=conn(NI,NI,pcon)*gII
    Iapp=drive+0.3*rng.standard_normal(N)
    def rates(V):
        an=0.01*(V+34)/(1-np.exp(-(V+34)/10));bn=0.125*np.exp(-(V+44)/80)
        am=0.1*(V+30)/(1-np.exp(-(V+30)/10));bm=4*np.exp(-(V+55)/18)
        ah=0.07*np.exp(-(V+44)/20);bh=1/(1+np.exp(-(V+14)/10));return an,bn,am,bm,ah,bh
    V=-67.0+np.zeros(N);n=0.07+np.zeros(N);h=0.98+np.zeros(N);Nai=18.0+np.zeros(N);Ko=4.0
    gE=np.zeros(N);gI=np.zeros(N);spk_prev=np.zeros(N,bool)
    dt=0.025;T=30000.0;arrest=10000.0;nstep=int(T/dt);rec_every=int(4.0/dt)
    nrec=nstep//rec_every;Vchan=np.zeros((nrec,N),np.float32);pop=np.zeros(nrec);k=0
    for i in range(nstep):
        t=i*dt;ox=1.0 if t<arrest else 0.0
        Ki=140.0+(18.0-Nai);Nao=144.0-beta*(Nai-18.0)
        ENa=26.64*np.log(Nao/Nai);EK=26.64*np.log(Ko/Ki);ECl=26.64*np.log(Cl_i/Cl_o)
        an,bn,am,bm,ah,bh=rates(V);minf=am/(am+bm)
        INa=gNa*minf**3*h*(V-ENa)+gNaL*(V-ENa);IK=(gK*n**4+gKL)*(V-EK);ICl=gClL*(V-ECl)
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
            sE=spk&isE;sI=spk&isI
            if sE.any(): gE[:NE]+=WEE@sE[:NE];gE[NE:]+=WIE@sE[:NE]
            if sI.any(): gI[:NE]+=WEI@sI[NE:];gI[NE:]+=WII@sI[NE:]
        spk_prev=(V>-20.0)
        if i%rec_every==0 and k<nrec: Vchan[k]=V;pop[k]=spk.sum();k+=1
    tt=np.arange(nrec)/FS;return Vchan,pop,tt,arrest/1000.0

def label_windows(Vchan,pop,tt,arrest):
    rp=np.convolve(pop,np.ones(20)/20,'same');pidx=np.where(tt>=arrest)[0]
    pkt=tt[pidx[rp[pidx].argmax()]];T=tt[-1]
    regions={0:(4.0,9.5),1:(pkt-0.75,pkt+0.75),2:(T-3.3,T-0.2)}
    X,y=[],[]
    for lab,(a,b) in regions.items():
        idx=np.where((tt>=a)&(tt<b))[0]
        for s in range(idx[0],idx[-1]-WIN,STRIDE):
            X.append(Vchan[s:s+WIN].T);y.append(lab)   # (125,WIN)
    return np.array(X,np.float16),np.array(y,np.int8)

allX=[];ally=[];allrun=[];rid=0
for drive,seed in itertools.product(DRIVES,SEEDS):
    Vchan,pop,tt,arrest=simulate(drive,seed)
    X,y=label_windows(Vchan,pop,tt,arrest)
    allX.append(X);ally.append(y);allrun.append(np.full(len(y),rid,np.int16))
    print(f"run {rid:2d} drive={drive} seed={seed}: {len(y)} windows  classes={np.bincount(y,minlength=3)}",flush=True)
    rid+=1
X=np.concatenate(allX);y=np.concatenate(ally);run_id=np.concatenate(allrun)
np.savez_compressed("results/dataset.npz",X=X,y=y,run_id=run_id,
                    drives=DRIVES,seeds=SEEDS,WIN=WIN,FS=FS)
print(f"\nDATASET: X={X.shape} {X.dtype}  y classes={np.bincount(y)}  runs={rid}")
print("saved results/dataset.npz")
