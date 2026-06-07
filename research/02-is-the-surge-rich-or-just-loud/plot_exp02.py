"""Figure for Exp 02: the surge is loud + synchronous but LOW-complexity.
Usage: py plot_exp02.py"""
import numpy as np, json
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
d=np.load("results/exp02_seed1.npz"); Vchan=d["Vchan"]; tt=d["tt"]; arrest=float(d["arrest"]); pkt=float(d["pkt"])
recs=[json.loads(l) for l in open("results/exp02_summary.jsonl")]
order=["baseline","surge","silence"]
def col(metric): return {w:[r[w][metric] for r in recs] for w in order}
LZ=col("LZc"); SY=col("synchrony"); PW=col("power")

fig=plt.figure(figsize=(11,7))
# A: heatmap of per-neuron V over the whole run
axA=fig.add_subplot(2,1,1)
im=axA.imshow(Vchan.T,aspect="auto",cmap="viridis",extent=[tt[0],tt[-1],0,Vchan.shape[1]],
              vmin=-75,vmax=-20,origin="lower")
axA.axvline(arrest,color="w",ls="--",lw=1); axA.axvline(pkt,color="crimson",ls=":",lw=1.5)
axA.set_ylabel("neuron #"); axA.set_xlabel("time (s)")
axA.set_title("Per-neuron membrane potential: baseline speckle (diverse) → surge stripes "
              "(everyone together) → silence (flat)")
fig.colorbar(im,ax=axA,label="V (mV)",pad=0.01)

def bars(ax,data,title,ylab,colors):
    means=[np.mean(data[w]) for w in order]; lo=[means[i]-min(data[order[i]]) for i in range(3)]
    hi=[max(data[order[i]])-means[i] for i in range(3)]
    ax.bar(order,means,yerr=[lo,hi],capsize=4,color=colors)
    ax.set_title(title); ax.set_ylabel(ylab)
axB=fig.add_subplot(2,3,4); bars(axB,LZ,"Complexity (LZc)\nlow = ordered/uniform","normalized LZc",["#1f77b4","crimson","gray"])
axB.axhline(0,color="k",lw=0.5)
axC=fig.add_subplot(2,3,5); bars(axC,SY,"Synchrony\nhigh = everyone together","synchrony index",["#1f77b4","crimson","gray"])
axD=fig.add_subplot(2,3,6); bars(axD,PW,"Power\n(loudness)","mean V variance",["#1f77b4","crimson","gray"])
fig.tight_layout(); fig.savefig("results/figure_exp02.png",dpi=130)
print("wrote results/figure_exp02.png")
print("mean LZc  baseline=%.2f surge=%.2f silence=%.2f"%(np.mean(LZ['baseline']),np.mean(LZ['surge']),np.mean(LZ['silence'])))
print("mean sync baseline=%.2f surge=%.2f"%(np.mean(SY['baseline']),np.mean(SY['surge'])))
