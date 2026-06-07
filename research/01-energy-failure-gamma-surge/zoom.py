"""Is the surge genuine gamma OSCILLATION or a single broadband blip?
Compare raw pop-rate waveform + spectrum: baseline window vs surge window."""
import numpy as np, sys
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
tag=sys.argv[1] if len(sys.argv)>1 else "d2.2"
d=np.load(f"results/net_{tag}.npz"); pop=d["pop"]; rec_dt=float(d["rec_dt"])
arrest=float(d["arrest"])/1000.0; fs=1000.0/rec_dt
t=np.arange(len(pop))*rec_dt/1000.0
a=np.load(f"results/analysis_{tag}.npz"); pkt=float(a["pkt"])

def win(c,half=0.6):
    m=(t>=c-half)&(t<=c+half); return t[m],pop[m]
def spec(x):
    x=x-x.mean(); f=np.fft.rfftfreq(len(x),1/fs); P=np.abs(np.fft.rfft(x*np.hanning(len(x))))**2
    return f,P

# baseline window (mid-baseline) and surge window (around peak)
tb,xb=win(6.5); ts,xs=win(pkt)
fb,Pb=spec(xb); fsp,Ps=spec(xs)

def peakband(f,P,lo=25,hi=120):
    m=(f>=lo)&(f<hi); fp=f[m][P[m].argmax()]; return fp,P[m].max()
fpb,_=peakband(fb,Pb); fps,_=peakband(fsp,Ps)

fig,ax=plt.subplots(2,2,figsize=(11,6))
ax[0,0].plot(tb,xb,lw=0.7,color="#1f77b4"); ax[0,0].set_title(f"baseline pop rate (~6.5s)"); ax[0,0].set_ylabel("spikes/ms")
ax[0,1].plot(ts,xs,lw=0.7,color="crimson"); ax[0,1].set_title(f"surge pop rate (~{pkt:.1f}s, +{pkt-arrest:.1f}s post-arrest)")
ax[1,0].semilogy(fb,Pb,color="#1f77b4"); ax[1,0].set_xlim(0,150); ax[1,0].axvspan(25,100,color="cyan",alpha=0.15)
ax[1,0].set_title(f"baseline spectrum (peak in 25-120Hz: {fpb:.0f} Hz)"); ax[1,0].set_xlabel("Hz")
ax[1,1].semilogy(fsp,Ps,color="crimson"); ax[1,1].set_xlim(0,150); ax[1,1].axvspan(25,100,color="cyan",alpha=0.15)
ax[1,1].set_title(f"surge spectrum (peak in 25-120Hz: {fps:.0f} Hz)"); ax[1,1].set_xlabel("Hz")
fig.tight_layout(); fig.savefig("results/figure_zoom.png",dpi=130)
# count oscillation cycles in surge window: zero-crossings of mean-subtracted, smoothed signal
xss=np.convolve(xs-xs.mean(),np.ones(3)/3,'same'); zc=np.sum(np.diff(np.sign(xss))!=0)
print(f"baseline gamma-band peak freq = {fpb:.0f} Hz")
print(f"surge    gamma-band peak freq = {fps:.0f} Hz")
print(f"surge window length {ts[-1]-ts[0]:.2f}s, sign-changes={zc} -> ~{zc/2} oscillation cycles")
print(f"surge peak-band power / baseline peak-band power = {Ps[(fsp>=25)&(fsp<100)].max()/max(Pb[(fb>=25)&(fb<100)].max(),1e-12):.1f}x")
print("wrote results/figure_zoom.png")
