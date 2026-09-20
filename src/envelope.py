"""Envelope analysis and resonance-band selection.

These are the functions notebooks 04-06 converged on. They were written three
times in the notebooks before being moved here.

The chain is: band-pass the record to a resonance band, take the Hilbert
envelope, transform it, and read the amplitude at the fault frequencies the
bearing's geometry predicts. What makes a band good is that the fault
frequency and its harmonics stand out from the local background; `comb_score`
measures that without being told which fault is present, which is the part
that lets the band be chosen honestly.
"""

import numpy as np
from scipy.signal import butter, filtfilt, hilbert

FS = 12000
FAULT_KEYS = ("BPFO", "BPFI", "BSF")

# filtfilt rings at the record's ends, and a narrow band rings for a long
# time. Those transients are impulsive enough to dominate kurtosis and to
# leak into the envelope, so a margin is dropped from each end before
# anything is measured.
EDGE_FRACTION = 0.05


def band_pass(x, band, fs=FS, order=4, trim=EDGE_FRACTION):
    """Zero-phase band-pass, with the filter's edge transients cut off."""
    nyq = fs / 2
    b, a = butter(order, [band[0] / nyq, band[1] / nyq], btype="band")
    y = filtfilt(b, a, x)
    k = int(trim * len(y))
    return y[k:len(y) - k] if k else y


def envelope(x, band, fs=FS, order=4, trim=EDGE_FRACTION):
    """Hilbert envelope of the band-passed record."""
    return np.abs(hilbert(band_pass(x, band, fs, order, trim)))


def envelope_spectrum(x, band, fs=FS, order=4, trim=EDGE_FRACTION):
    """Amplitude spectrum of the envelope. Returns (frequencies, amplitudes).

    The envelope's mean is removed: it is a magnitude, so it is strictly
    positive, and leaving it in puts a peak at 0 Hz taller than anything else
    in the spectrum.
    """
    env = envelope(x, band, fs, order, trim)
    env = env - env.mean()
    n = len(env)
    f = np.fft.rfftfreq(n, 1 / fs)
    a = np.abs(np.fft.rfft(env * np.hanning(n))) / n * 4
    return f, a


def peak_ratio(f, a, f0, tol=2.5, bg=(10, 60)):
    """How far a peak at f0 stands above its own neighbourhood.

    The background is the median over a ring around f0 rather than the whole
    spectrum, so the number says "this line is taller than the lines beside
    it" - which is what makes a peak believable - instead of "this line is
    tall compared with the record's loudest component".
    """
    near = np.abs(f - f0) <= tol
    if not near.any():
        return 0.0
    ring = (np.abs(f - f0) > bg[0]) & (np.abs(f - f0) < bg[1])
    return float(a[near].max() / np.median(a[ring]))


def comb_score(f, a, f0, harmonics=4, tol=2.5):
    """Geometric mean of the peak ratios at f0, 2*f0, ... harmonics*f0.

    A single tall line can be a machine line, a resonance, or luck. A line
    with harmonics behind it is a periodic impact. The geometric mean is used
    rather than the arithmetic one because it demands every harmonic be
    present - one missing harmonic pulls the score down, where a mean would
    let a single large value carry it.
    """
    rs = [peak_ratio(f, a, k * f0, tol) for k in range(1, harmonics + 1)
          if k * f0 < f[-1]]
    if not rs:
        return 0.0
    return float(np.exp(np.mean(np.log(np.maximum(rs, 1e-3)))))


def score_band(x, band, fault_freqs, fs=FS, **kw):
    """Score one band without being told which fault is present.

    The three candidate frequencies come from the bearing's geometry and the
    shaft speed, both known before any diagnosis. Which of the three is
    faulted is not known, so every candidate is scored and the best one is
    returned along with its name.
    """
    f, a = envelope_spectrum(x, band, fs, **kw)
    scores = {k: comb_score(f, a, fault_freqs[k]) for k in FAULT_KEYS}
    best = max(scores, key=scores.get)
    return scores[best], best, scores


def band_grid(widths=(500, 1000, 2000), step=250, low=250, high=5800):
    """Candidate bands: each width slid across the spectrum in fixed steps."""
    out = set()
    for w in widths:
        centre = w / 2 + low
        while centre + w / 2 <= high:
            out.add((round(centre - w / 2), round(centre + w / 2)))
            centre += step
    return sorted(out)


def select_band(x, fault_freqs, grid=None, fs=FS, **kw):
    """Search the grid for the band whose envelope spectrum is most convincing.

    Returns (band, score, fault_name, all_rows). The search is blind to which
    fault is present but not to the bearing's geometry - see `score_band`.

    Note that searching a grid inflates the winning score even on a healthy
    record, because the maximum of many noisy numbers is larger than any one
    of them. The threshold this score must clear has to be calibrated by
    running the same search on a healthy record, not assumed.
    """
    grid = grid or band_grid()
    rows = []
    for band in grid:
        score, which, _ = score_band(x, band, fault_freqs, fs, **kw)
        rows.append((band, score, which))
    band, score, which = max(rows, key=lambda r: r[1])
    return band, score, which, rows
