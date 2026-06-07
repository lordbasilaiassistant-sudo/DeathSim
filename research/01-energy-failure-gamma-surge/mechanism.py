"""The causal mechanism: firing rate is a NON-MONOTONIC function of [K]_o.
As anoxia drives [K]_o up, the network passes through a hyperexcitable window
(the surge) before high [K]_o forces depolarization block (silence).
This is why energy failure ALONE yields surge-then-silence. Usage: py mechanism.py d2.2"""
import numpy as np, sys
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
tag=sys.argv[1] if len(sys.argv)>1 else "d2.2"
d=np.load(f"results/net_{tag}.npz"); pop=d["pop"]; Ko=d["Ko"]; rec_dt=float(d["rec_dt"])
arrest=float(d["arrest"])/1000.0; t=np.arange(len(pop))*rec_dt/1000.0
post=t>=arrest
r=np.convolve(pop,np.ones(50)/50,'same')  # ~50ms smoothing -> rate
Kp=Ko[post]; rp=r[post]
bins=np.linspace(4,Kp.max(),40); idx=np.digitize(Kp,bins)
mean_r=np.array([rp[idx==i].mean() if np.any(idx==i) else np.nan for i in range(1,len(bins))])
ctr=0.5*(bins[1:]+bins[:-1])
peakK=ctr[np.nanargmax(mean_r)]
fig,ax=plt.subplots(1,2,figsize=(11,4))
ax[0].plot(t,Ko,color="#d62728"); ax[0].set_xlabel("time (s)"); ax[0].set_ylabel("[K$^+$]$_o$ (mM)")
ax[0].axvline(arrest,color="k",ls="--",lw=1); ax[0].set_title("[K$^+$]$_o$ rises monotonically after arrest")
ax[1].plot(ctr,mean_r,"o-",color="#6a3d9a")
ax[1].axvline(peakK,color="crimson",ls=":",label=f"peak firing at [K]$_o$≈{peakK:.0f} mM")
ax[1].set_xlabel("[K$^+$]$_o$ (mM)"); ax[1].set_ylabel("mean firing rate (spikes/ms)")
ax[1].set_title("Firing rate vs [K$^+$]$_o$: hyperexcitable window then depolarization block")
ax[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig("results/figure_mechanism.png",dpi=130)
print(f"peak firing at [K]_o ~ {peakK:.1f} mM; rate at max [K]_o ({Kp.max():.0f} mM) = {mean_r[-1]:.3f} spikes/ms")
print("inverted-U (surge then block):", bool(np.nanargmax(mean_r) not in (0,len(mean_r)-1)))
print("wrote results/figure_mechanism.png")
