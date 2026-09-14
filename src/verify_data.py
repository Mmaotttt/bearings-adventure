"""Sanity check on the downloaded files: does every one load, is it on the
12 kHz grid after correction, and where do its fault frequencies fall?"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import cwru_io

DATA = Path(__file__).parent.parent / "data"

FILES = [
    ("normal_1hp_98.mat",    "Normal, 1 hp",                True),
    ("OR007at6_1hp_131.mat", "Outer race 0.007in @6, 1 hp", False),
    ("IR007_1hp_106.mat",    "Inner race 0.007in, 1 hp",    False),
    ("B007_1hp_119.mat",     "Ball 0.007in, 1 hp",          False),
]


def load_all():
    out = []
    for fname, label, is_baseline in FILES:
        loader = cwru_io.load_baseline if is_baseline else cwru_io.load
        out.append(loader(DATA / fname, name=label))
    return out


if __name__ == "__main__":
    print(f"{'file':<24}{'variable':<15}{'samples':>8}{'fs':>7}{'s':>7}{'rpm':>7}"
          f"{'BPFO':>8}{'BPFI':>8}{'BSF':>8}")
    print("-" * 92)
    for sig in load_all():
        f = sig.fault_freqs()
        print(f"{sig.path.name:<24}{sig.key:<15}{len(sig.x):>8}{sig.fs:>7}"
              f"{sig.duration:>7.2f}{sig.rpm:>7.0f}"
              f"{f['BPFO']:>8.1f}{f['BPFI']:>8.1f}{f['BSF']:>8.1f}")

    rates = {s.fs for s in load_all()}
    assert rates == {cwru_io.FS}, f"records are not on one grid: {rates}"
    print(f"\nall four on the {cwru_io.FS} Hz grid, comparable.")
