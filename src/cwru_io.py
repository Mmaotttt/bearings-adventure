"""Loading CWRU Bearing Data Center .mat files.

The variable names inside each .mat carry the file number as a prefix
(X097_DE_time, X130_DE_time, ...), so nothing may be hard-coded: every
channel is located by suffix instead.

Channels: DE = drive-end accelerometer, FE = fan-end, BA = base plate.
This project uses DE only.

Two quirks of the normal baseline files (97-100), established by inspection
rather than taken from the documentation, which does not state the baseline
rate:

  * They are sampled at 48 kHz, not the 12 kHz of the 12k fault set. Three
    machine lines that sit at 145.7 / 159.5 / 189.1 Hz in the fault records
    land there in a baseline file only when it is read as 48 kHz; read as
    12 kHz they collapse to a quarter of those frequencies. The durations
    agree too - 10.08 s against the fault set's 10.17 s. So the baseline is
    decimated by 4 before any comparison with a fault record.
  * They carry no RPM variable and no BA channel, so the speed comes from
    the load table on the CWRU site instead.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.io import loadmat
from scipy.signal import decimate

FS = 12000       # Hz, the 12k drive-end fault set
FS_BASELINE = 48000  # Hz, the normal baseline files - see module docstring

# Approximate shaft speeds per motor load, from the CWRU data tables. Needed
# only for the baseline files, which carry no RPM variable; every fault file
# reports its own speed and that value is always preferred.
RPM_BY_LOAD = {0: 1797, 1: 1772, 2: 1750, 3: 1730}

# SKF 6205-2RS JEM, drive end. Multiples of shaft rate n = rpm / 60.
# Source: CWRU Bearing Data Center, bearing information page.
FAULT_MULTIPLIERS = {
    "BPFO": 3.5848,    # outer race
    "BPFI": 5.4152,    # inner race
    "BSF": 4.7135,     # ball (rolling element)
    "FTF": 0.39828,    # cage
}


@dataclass
class Signal:
    """One drive-end acceleration record plus the metadata a plot needs."""

    name: str          # short label used in figures, e.g. "OR007 @6, 1 hp"
    path: Path
    x: np.ndarray      # drive-end acceleration, 1-D
    fs: int            # sampling rate, Hz
    rpm: float         # shaft speed
    key: str           # the .mat variable the samples came from

    @property
    def n(self) -> float:
        """Shaft rate in Hz."""
        return self.rpm / 60.0

    @property
    def duration(self) -> float:
        return len(self.x) / self.fs

    def fault_freqs(self) -> dict[str, float]:
        """Theoretical fault frequencies in Hz at this record's own speed."""
        return {k: m * self.n for k, m in FAULT_MULTIPLIERS.items()}

    def __repr__(self) -> str:
        return (f"Signal({self.name!r}, {len(self.x)} samples, "
                f"{self.duration:.2f} s, {self.rpm:.0f} rpm)")


def _find(mat: dict, suffix: str) -> list[str]:
    return sorted(k for k in mat if not k.startswith("__") and k.endswith(suffix))


def _id_from_name(path: Path):
    """The CWRU file id, taken from the trailing number in the filename."""
    m = re.search(r"(\d+)$", path.stem)
    return int(m.group(1)) if m else None


def _select(mat: dict, suffix: str, path: Path, cwru_id=None):
    """Pick the one variable of this kind that belongs to *this* record.

    Normally a file holds a single channel of each kind. File 99 does not: it
    carries X099_DE_time and also a complete copy of X098_DE_time, byte for
    byte identical to file 98's. Taking the first key alphabetically hands
    back file 98's data under file 99's name - two records that are the same
    samples wearing different labels, which is exactly the leak that makes a
    classifier look better than it is.

    So when the file id is known, the variable carrying that id wins.
    """
    keys = _find(mat, suffix)
    if not keys:
        return None
    if len(keys) == 1:
        return keys[0]

    if cwru_id is None:
        cwru_id = _id_from_name(path)
    if cwru_id is not None:
        exact = [k for k in keys if k.startswith(f"X{cwru_id:03d}")]
        if len(exact) == 1:
            return exact[0]

    raise KeyError(
        f"{path.name}: {len(keys)} candidates for *{suffix} ({keys}) and no "
        f"file id to choose between them - pass cwru_id explicitly")


def load(path, name=None, fs=FS, default_rpm=None, decimate_to=None,
         cwru_id=None) -> Signal:
    """Read the drive-end channel out of a CWRU .mat file.

    The RPM is taken from the file itself when present: the four load
    settings run at roughly 1797 / 1772 / 1750 / 1730 rpm, and treating
    the speed as a constant shifts every theoretical fault frequency.

    ``decimate_to`` resamples the record down to that rate (an integer
    factor, anti-aliased) - used to bring a 48 kHz baseline file onto the
    12 kHz grid of the fault files so the two can be plotted together.
    """
    path = Path(path)
    mat = loadmat(path)

    key = _select(mat, "DE_time", path, cwru_id)
    if key is None:
        raise KeyError(f"{path.name}: no *DE_time variable, found {_find(mat, '')}")
    x = np.asarray(mat[key]).ravel().astype(np.float64)

    rpm_key = _select(mat, "RPM", path, cwru_id)
    if rpm_key:
        rpm = float(np.asarray(mat[rpm_key]).ravel()[0])
    elif default_rpm is not None:
        rpm = float(default_rpm)
    else:
        raise KeyError(f"{path.name}: no RPM variable and no default_rpm given")

    if decimate_to is not None and decimate_to != fs:
        q, rem = divmod(fs, decimate_to)
        if rem or q < 1:
            raise ValueError(f"{fs} Hz is not an integer multiple of {decimate_to} Hz")
        x = decimate(x, q, ftype="fir", zero_phase=True)
        fs = decimate_to

    return Signal(name=name or path.stem, path=path, x=x, fs=fs, rpm=rpm, key=key)


def load_baseline(path, name=None, load_hp=1, decimate_to=FS, cwru_id=None) -> Signal:
    """Read a normal baseline file, correcting for its quirks.

    Besides the 48 kHz rate and the missing RPM, note that these four records
    are not all the same length: file 97 runs 5.08 s where the others run
    about 10. The rate is not in question - six machine lines land where a
    known 12 kHz record puts them only when 97 is read as 48 kHz - it is
    simply a shorter recording.
    """
    return load(path, name=name, fs=FS_BASELINE,
                default_rpm=RPM_BY_LOAD[load_hp], decimate_to=decimate_to,
                cwru_id=cwru_id)


def channels(path) -> dict[str, int]:
    """Every non-metadata variable in a .mat and its length — for inspection."""
    mat = loadmat(path)
    return {k: np.asarray(v).size for k, v in mat.items() if not k.startswith("__")}
