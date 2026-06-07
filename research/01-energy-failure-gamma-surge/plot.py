"""Main figure: the energy-failure gamma surge. Usage: py plot.py d2.2"""
import numpy as np, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
tag=sys.argv[1] if len(sys.argv)>1 else "d2.2"
a=np.load(f"results/analysis_{tag}.npz")
t=a["t"]; r=a["r"]; Ko=a["Ko"]; Vm=a["Vm"]; tt=a["tt"]; gamma_t=a["gamma_t"]
f=a["f"]; Sxx=a["Sxx"]; arrest=float(a["arrest"]); pkt=float(a["pkt"])
silence=float(a["silence_t"]); tgmax=float(a["tgmax"])

fig,ax=plt.subplots(4,1,figsize=(9,10),sharex=True)
def marks(x):
    x.axvline(arrest,color="k",ls="--",lw=1,label="cardiac arrest (O2->0)")
    x.axvline(tgmax,color="crimson",ls=":",lw=1.5,label="gamma surge peak")
    x.axvline(silence,color="dimgray",ls=":",lw=1.5,label="isoelectric silence")

ax[0].plot(t,r,color="#1f77b4",lw=0.8); ax[0].set_ylabel("pop. firing\n(spikes/ms)")
ax[0].set_title("Energy failure alone reproduces the dying-brain gamma surge\n"
                "biophysical E/I network, no consciousness in the model",fontsize=11)
marks(ax[0]); ax[0].legend(fontsize=7,loc="upper left")

ax[1].plot(t,Ko,color="#d62728",lw=1); ax[1].set_ylabel("[K$^+$]$_o$ (mM)")
ax[1].axhline(4,color="gray",lw=0.5,ls=":"); marks(ax[1])
ax[1].annotate("anoxic depolarization\n(ion gradients collapse)",
               xy=(pkt,Ko.max()*0.9),fontsize=8,color="#d62728")

ax[2].plot(t,Vm,color="#2ca02c",lw=1); ax[2].set_ylabel("mean V (mV)")
ax[2].annotate("depolarization block\n= electrical silence",xy=(silence+1,Vm[-1]),
               fontsize=8,color="#2ca02c"); marks(ax[2])

# spectrogram
ex=[tt.min(),tt.max(),f.min(),min(f.max(),150)]
S=10*np.log10(Sxx+1e-12); fm=f<=150
im=ax[3].pcolormesh(tt,f[fm],S[fm],shading="auto",cmap="magma")
ax[3].set_ylabel("freq (Hz)"); ax[3].set_xlabel("time (s)")
ax[3].axhspan(25,100,color="cyan",alpha=0.12)
marks(ax[3]); ax[3].set_ylim(0,150)
fig.colorbar(im,ax=ax[3],label="power (dB)",pad=0.01)
fig.tight_layout()
fig.savefig("results/figure_main.png",dpi=130)
print("wrote results/figure_main.png")

# second figure: gamma power timecourse, baseline vs surge
fig2,bx=plt.subplots(figsize=(8,3.2))
bx.plot(tt,gamma_t,color="crimson",lw=1.2)
bx.axvline(arrest,color="k",ls="--",lw=1); bx.set_yscale("log")
bx.set_xlabel("time (s)"); bx.set_ylabel("gamma (25-100Hz) power")
bx.set_title("Gamma-band power: modest baseline -> transient post-arrest surge -> silence")
gbase=tt<arrest
bx.axhline(np.median(gamma_t[gbase]),color="gray",ls=":",lw=1,label="baseline median")
bx.legend(fontsize=8); fig2.tight_layout(); fig2.savefig("results/figure_gamma.png",dpi=130)
print("wrote results/figure_gamma.png")
