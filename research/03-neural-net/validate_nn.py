"""
20-LINE-TEST for the NN idea: is the dying-brain state even LEARNABLE from the raw
multichannel signal, and does it GENERALIZE across runs?

Data: the Exp-02 simulations (per-neuron V, 125 ch @ 250 Hz). Slice short windows,
label each by regime {baseline=waking-like, surge, silence}. Train a small MLP on
seeds 1-3, TEST on seed 4 (a network it never saw). If test accuracy >> chance, the
signal is learnable and the full dataset-sweep + classifier plan is justified.

This is a proof-of-learnability, NOT the final model. No real EEG yet (that's Stage 2).
"""
import numpy as np, glob, os, torch, torch.nn as nn
torch.manual_seed(0); np.random.seed(0)
DD=os.path.join(os.path.dirname(__file__),"..","02-is-the-surge-rich-or-just-loud","results")
WIN=48; STRIDE=8; FS=250.0  # 192 ms windows, 32 ms stride

def windows_from(npz):
    d=np.load(npz); V=d["Vchan"]; tt=d["tt"]; pkt=float(d["pkt"]); arr=float(d["arrest"]); T=tt[-1]
    regions={0:(4.0,9.5),          # baseline (waking-like)
             1:(pkt-0.75,pkt+0.75),# surge
             2:(T-3.3,T-0.2)}      # silence
    X,y=[],[]
    for lab,(a,b) in regions.items():
        idx=np.where((tt>=a)&(tt<b))[0]
        for s in range(idx[0],idx[-1]-WIN,STRIDE):
            X.append(V[s:s+WIN].T.reshape(-1))  # (125*48,)
            y.append(lab)
    return np.array(X,dtype=np.float32), np.array(y)

files=sorted(glob.glob(os.path.join(DD,"exp02_seed*.npz")))
assert len(files)>=4, f"need >=4 seed files, found {len(files)}"
tr=[windows_from(f) for f in files[:3]]; te=windows_from(files[3])
Xtr=np.concatenate([t[0] for t in tr]); ytr=np.concatenate([t[1] for t in tr])
Xte,yte=te
mu,sd=Xtr.mean(0),Xtr.std(0)+1e-6
Xtr=(Xtr-mu)/sd; Xte=(Xte-mu)/sd
print(f"train {Xtr.shape} (seeds 1-3)  test {Xte.shape} (seed 4 held out)  classes={np.bincount(ytr)}")

net=nn.Sequential(nn.Linear(Xtr.shape[1],128),nn.ReLU(),nn.Dropout(0.3),
                  nn.Linear(128,64),nn.ReLU(),nn.Linear(64,3))
opt=torch.optim.Adam(net.parameters(),1e-3,weight_decay=1e-4)
lossf=nn.CrossEntropyLoss()
Xt=torch.tensor(Xtr); yt=torch.tensor(ytr); Xv=torch.tensor(Xte); yv=torch.tensor(yte)
for ep in range(60):
    net.train(); perm=torch.randperm(len(Xt))
    for i in range(0,len(Xt),64):
        b=perm[i:i+64]; opt.zero_grad()
        l=lossf(net(Xt[b]),yt[b]); l.backward(); opt.step()
net.eval()
with torch.no_grad():
    pr=net(Xv).argmax(1).numpy()
acc=(pr==yte).mean(); chance=np.bincount(yte).max()/len(yte)
cm=np.zeros((3,3),int)
for t,p in zip(yte,pr): cm[t,p]+=1
names=["baseline","surge","silence"]
print(f"\nHELD-OUT (seed 4) accuracy = {acc*100:.1f}%   (chance = {chance*100:.1f}%)")
print("confusion (rows=true, cols=pred):"); print("           "+"  ".join(f"{n:>8}" for n in names))
for i,n in enumerate(names): print(f"{n:>9}  "+"  ".join(f"{cm[i,j]:8d}" for j in range(3)))
surge_recall=cm[1,1]/cm[1].sum()
print(f"\nsurge detected (recall) = {surge_recall*100:.1f}%")
print("VALIDATION:", "PASS - dying-state is learnable & generalizes across runs"
      if acc>chance+0.2 else "WEAK - not clearly learnable")
