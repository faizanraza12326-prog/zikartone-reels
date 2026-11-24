"""Sound for quiz reels (no music): whoosh on each new question, ticks on the countdown
(sharper in the last 3 seconds), a bell chime on the answer, swells on intro/outro.
Output is loudness-normalised to -14 LUFS, the level Instagram/YouTube/TikTok aim for."""
import json, os, sys, subprocess
import numpy as np

SR = 44100
INTRO, ASK, REVEAL, OUTRO = 2.6, 8, 2.6, 4.5
rng = np.random.default_rng(7)

def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))

def tick(strong=False):
    n = int(.09 * SR); t = np.arange(n) / SR
    f = 1900 if strong else 1350
    body = np.sin(2 * np.pi * f * t) * env_exp(n, .018)
    click = rng.standard_normal(n) * env_exp(n, .004) * .5
    low = np.sin(2 * np.pi * (f / 2) * t) * env_exp(n, .03) * .6
    return (body + click + low) * (1.0 if strong else .75)

def whoosh(d=.55):
    n = int(d * SR); x = rng.standard_normal(n)
    # crude band-pass sweep: moving average of decreasing width
    out = np.zeros(n); w0, w1 = 40, 4
    for i in range(0, n, 512):
        w = int(w0 + (w1 - w0) * i / n)
        seg = x[i:i + 512]
        out[i:i + 512] = np.convolve(seg, np.ones(w) / w, mode='same')
    shape = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return out * shape * 2.2

def bell(freqs, d=1.6, tau=.45):
    n = int(d * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for k, f in enumerate(freqs):
        s += np.sin(2 * np.pi * f * t) * (1 / (k + 1)) + .25 * np.sin(2 * np.pi * f * 2.76 * t) * env_exp(n, tau / 3)
    attack = np.minimum(1, np.arange(n) / (.004 * SR))
    return s * env_exp(n, tau) * attack

def swell(d=1.4, f=220):
    n = int(d * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * m * t) / m for m in (1, 1.5, 2, 3))
    return s * np.sin(np.pi * np.linspace(0, 1, n)) ** 2 * .5

def build(n_q, out_wav):
    total = INTRO + n_q * (ASK + REVEAL) + OUTRO
    buf = np.zeros(int(total * SR) + SR)
    def add(at, x, g=1.0):
        s = int(at * SR); buf[s:s + len(x)] += x[:len(buf) - s] * g
    add(0, swell(2.2, 196), .8); add(.15, bell([784, 988, 1175], 1.8), .5)
    for q in range(n_q):
        st = INTRO + q * (ASK + REVEAL)
        add(st, whoosh(), .9)
        for sec in range(ASK):
            add(st + sec + .02, tick(sec >= ASK - 3))
        add(st + ASK, bell([1047, 1319, 1568]), .9)          # C6 E6 G6
        add(st + ASK + .02, whoosh(.3), .4)
    end = INTRO + n_q * (ASK + REVEAL)
    add(end, whoosh(.7), .9); add(end + .2, bell([523, 659, 784, 1047], 2.6, .7), .8); add(end, swell(3.5, 262), .7)
    buf = buf / (np.abs(buf).max() + 1e-9) * .9
    raw = out_wav + '.raw.wav'
    import wave
    with wave.open(raw, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((buf * 32000).astype('<i2').tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.0:LRA=11,volume=3.2dB,alimiter=limit=0.8:level=false', '-ar', str(SR), out_wav], check=True)
    os.remove(raw)
    return total

if __name__ == '__main__':
    q = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'quiz.json'))
    print(build(len(q), 'audio.wav'))
