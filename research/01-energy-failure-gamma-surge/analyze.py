"""Analyze a network run: timeline of the surge, and whether it PRECEDES silence."""
import numpy as np, sys
from scipy.signal import spectrogram
d=np.load(f"results/net_{sys.argv[1] if len(sys.argv)>1 else 'base'}.npz")
pop=d["pop"]; Ko=d["Ko"]; Vm=d["Vmean"]; rec_dt=float(d["rec_dt"]); arrest=float(d["arrest"])
fs=1000.0/rec_dt; t=np.arange(len(pop))*rec_dt/1000.0  # s
tA=arrest/1000.0

# smoothed population rate (Hz-ish, spikes/bin)
def smooth(x,w):
    k=np.ones(w)/w; return np.convolve(x,k,'same')
r=smooth(pop,20)

# gamma-band (25-100 Hz) power over time via spectrogram of pop signal
f,tt,Sxx=spectrogram(pop-pop.mean(), fs=fs, nperseg=512, noverlap=384)
gband=(f>=25)&(f<100); hf=(f>=100)
gamma_t=Sxx[gband].sum(0); hf_t=Sxx[hf].sum(0); tt_s=tt

# windows
base=(t>4)&(t<tA); post=(t>=tA)
# silence onset = first time after arrest the smoothed rate drops below 5% of its post-arrest peak and stays there
post_idx=np.where(t>=tA)[0]
rp=r[post_idx]; pk=rp.max(); pkt=t[post_idx[rp.argmax()]]
thr=0.05*pk
below=post_idx[(r[post_idx]<thr)&(t[post_idx]>pkt)]
silence_t = t[below[0]] if len(below) else np.nan

# gamma timeline windows
gbase=tt_s<tA; gpost=tt_s>=tA
print(f"=== run: {sys.argv[1] if len(sys.argv)>1 else 'base'} (T={d['T']/1000:.0f}s, arrest@{tA:.0f}s, {float(d['temp'])}C) ===")
print(f"baseline pop rate (4-{tA:.0f}s): mean spk/ms={pop[base].mean():.3f}, active")
print(f"post-arrest peak pop rate: {pk:.2f} spk/ms at t={pkt:.2f}s  (+{pkt-tA:.2f}s after arrest)")
print(f"silence (rate<5% of peak) onset: t={silence_t:.2f}s  (+{silence_t-tA:.2f}s after arrest)" if not np.isnan(silence_t) else "no silence reached")
print(f"Ko: baseline {Ko[base].mean():.1f} -> peak {Ko.max():.1f} mM ; Vmean final {Vm[-1]:.1f} mV")
print(f"gamma(25-100Hz) power: baseline median={np.median(gamma_t[gbase]):.2f}, post-arrest MAX={gamma_t[gpost].max():.2f}  -> surge x{gamma_t[gpost].max()/max(np.median(gamma_t[gbase]),1e-9):.1f}")
tgmax=tt_s[gpost][gamma_t[gpost].argmax()]
print(f"gamma surge peak at t={tgmax:.2f}s (+{tgmax-tA:.2f}s)  ;  surge-precedes-silence: {tgmax < silence_t}")
np.savez(f"results/analysis_{sys.argv[1] if len(sys.argv)>1 else 'base'}.npz",
         t=t,r=r,Ko=Ko,Vm=Vm,tt=tt_s,gamma_t=gamma_t,hf_t=hf_t,f=f,Sxx=Sxx,
         arrest=tA,pkt=pkt,silence_t=silence_t,tgmax=tgmax)
