"""Turning a record into rows a classifier can learn from.

Each record is cut into fixed-length segments and each segment becomes one
row. Two families of features are computed, kept separable on purpose so the
notebook can ask what each family is worth:

  time      RMS, kurtosis, crest factor - what step 02 showed can detect a
            fault but never name one, because they ignore the order of the
            samples entirely.

  envelope  how far the envelope spectrum stands above its own local
            background at BPFO, BPFI, BSF and their second harmonics - the
            quantity steps 05 and 06 built. These do depend on order, and on
            the bearing's geometry, which is what lets them name a fault.

            Peak ratios rather than energy shares: a ratio is measured
            against the spectrum a few Hz away, so it survives a change in
            how hard the machine happens to be vibrating. A share is measured
            against the segment's own total, which mostly encodes load and
            fault size - the very things the classifier must not lean on if
            it is to work on a fault it has not seen. Measured across unseen
            fault diameters, ratios score 51 percent against shares' 42.

The fault frequencies are recomputed for every record: the four motor loads
run at four different speeds, so a frequency fixed at the 1 hp value would be
several Hz wrong at 3 hp - comparable to the resolution of a single segment.
"""

import numpy as np
from scipy.stats import kurtosis

import envelope as ev

SEGMENT = 2048          # 0.171 s at 12 kHz; a power of two for the FFT
BAND = (1000, 3000)     # the compromise band step 06 settled on
HARMONICS = (1, 2)

TIME_FEATURES = ["rms", "kurtosis", "crest"]
ENVELOPE_FEATURES = [f"{k}_x{h}" for k in ev.FAULT_KEYS for h in HARMONICS]
ALL_FEATURES = TIME_FEATURES + ENVELOPE_FEATURES


def segment(x, length=SEGMENT):
    """Cut into non-overlapping segments, dropping the remainder.

    Non-overlapping matters: overlapping windows share samples, so two rows
    built from them are not independent, and any split that puts one in
    training and the other in test has leaked.
    """
    n = len(x) // length
    return x[:n * length].reshape(n, length)


def time_features(seg):
    rms = np.sqrt(np.mean(seg ** 2))
    return [rms, kurtosis(seg, fisher=False), np.abs(seg).max() / rms]


def envelope_features(seg, fault_freqs, band=BAND, fs=ev.FS):
    """Peak-to-background ratio at each candidate fault frequency.

    Tolerances are in bins rather than Hz. A 2048-sample segment resolves
    5.9 Hz, so a fixed +/-2.5 Hz window would fall inside a single bin and a
    fixed 10-60 Hz background ring would hold only a handful - both fine for
    a ten-second record and useless for a segment.
    """
    # No edge trimming here - a 2048-sample segment cannot spare 10 percent,
    # and these segments come from the middle of a long record rather than
    # from a filter start-up, so the transient argument does not apply.
    f, a = ev.envelope_spectrum(seg, band, fs, trim=0.0)
    df = f[1] - f[0]
    return [ev.peak_ratio(f, a, h * fault_freqs[key],
                          tol=1.5 * df, bg=(4 * df, 40 * df))
            for key in ev.FAULT_KEYS for h in HARMONICS]


def record_rows(record, data_dir, length=SEGMENT, band=BAND):
    """Every segment of one record, as (features, metadata) lists."""
    sig = record.load_signal(data_dir)
    ff = sig.fault_freqs()
    rows, meta = [], []
    for i, seg in enumerate(segment(sig.x, length)):
        rows.append(time_features(seg) + envelope_features(seg, ff, band))
        meta.append(dict(file=record.filename, label=record.location,
                         load=record.load, size=record.size,
                         rpm=sig.rpm, segment=i))
    return np.array(rows), meta


def build_table(records, data_dir, length=SEGMENT, band=BAND, verbose=True):
    """Feature matrix, metadata, and the column names, over many records."""
    X, meta = [], []
    for r in records:
        rows, m = record_rows(r, data_dir, length, band)
        X.append(rows)
        meta.extend(m)
        if verbose:
            print(f"  {r.filename:<26} {len(rows):>4} segments  "
                  f"{m[0]['rpm']:.0f} rpm")
    return np.vstack(X), meta, list(ALL_FEATURES)
