"""The catalogue of CWRU records this project uses, and how to load them.

Forty records: a healthy baseline plus three fault locations at three fault
diameters, each at all four motor loads. Everything is the 12 kHz drive-end
set except the baselines, which are 48 kHz and get decimated on load.

Local files are named `<code>_<load>hp_<cwru id>.mat`. The id stays in the
name because the variables inside a .mat carry it as a prefix, so the id is
what ties a figure back to the row on the CWRU download page.
"""

from pathlib import Path

import cwru_io

# Approximate motor speed per load, from the CWRU tables. Only the baseline
# records need it - every fault record reports its own RPM, which is always
# preferred because the four loads run at four different speeds.
RPM_BY_LOAD = {0: 1797, 1: 1772, 2: 1750, 3: 1730}

# code -> (location, fault diameter in inches, which frequency it should show)
KINDS = {
    "normal":   ("healthy", 0.000, None),
    "IR007":    ("inner",   0.007, "BPFI"),
    "IR014":    ("inner",   0.014, "BPFI"),
    "IR021":    ("inner",   0.021, "BPFI"),
    "B007":     ("ball",    0.007, "BSF"),
    "B014":     ("ball",    0.014, "BSF"),
    "B021":     ("ball",    0.021, "BSF"),
    "OR007at6": ("outer",   0.007, "BPFO"),
    "OR014at6": ("outer",   0.014, "BPFO"),
    "OR021at6": ("outer",   0.021, "BPFO"),
}

# code -> {load: CWRU file id}, read off the download page on 2026-09-21.
IDS = {
    "normal":   {0: 97,  1: 98,  2: 99,  3: 100},
    "IR007":    {0: 105, 1: 106, 2: 107, 3: 108},
    "IR014":    {0: 169, 1: 170, 2: 171, 3: 172},
    "IR021":    {0: 209, 1: 210, 2: 211, 3: 212},
    "B007":     {0: 118, 1: 119, 2: 120, 3: 121},
    "B014":     {0: 185, 1: 186, 2: 187, 3: 188},
    "B021":     {0: 222, 1: 223, 2: 224, 3: 225},
    "OR007at6": {0: 130, 1: 131, 2: 132, 3: 133},
    "OR014at6": {0: 197, 1: 198, 2: 199, 3: 200},
    "OR021at6": {0: 234, 1: 235, 2: 236, 3: 237},
}


class Record:
    """One catalogue entry: what the record is, not its samples."""

    __slots__ = ("code", "load", "cwru_id", "location", "size", "fault_key")

    def __init__(self, code, load):
        self.code = code
        self.load = load
        self.cwru_id = IDS[code][load]
        self.location, self.size, self.fault_key = KINDS[code]

    @property
    def filename(self):
        return f"{self.code}_{self.load}hp_{self.cwru_id}.mat"

    @property
    def is_healthy(self):
        return self.location == "healthy"

    @property
    def label(self):
        """Short name for figures and tables."""
        if self.is_healthy:
            return f"healthy {self.load}hp"
        return f'{self.location} {self.size:.3f}" {self.load}hp'

    def load_signal(self, data_dir):
        """Read the samples. Baselines are decimated onto the 12 kHz grid."""
        path = Path(data_dir) / self.filename
        if self.is_healthy:
            return cwru_io.load_baseline(path, name=self.label,
                                         load_hp=self.load,
                                         cwru_id=self.cwru_id)
        return cwru_io.load(path, name=self.label, cwru_id=self.cwru_id)

    def __repr__(self):
        return f"Record({self.filename})"


def catalogue(loads=(0, 1, 2, 3), codes=None):
    """Every record, or the subset asked for."""
    codes = codes or list(IDS)
    return [Record(c, l) for c in codes for l in loads if l in IDS[c]]


def by_filename(data_dir=None):
    return {r.filename: r for r in catalogue()}
