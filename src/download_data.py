"""Fetch the CWRU records this project uses.

The .mat files are not kept in the repository - they are a few megabytes each
and belong to the Bearing Data Center, not to us. This script pulls them back.

    python src/download_data.py

File ids come from the tables at
<https://engineering.case.edu/bearingdatacenter/download-data-file>; the
condition each id corresponds to is recorded in data/FILES.md.
"""

import sys
import urllib.request
from pathlib import Path

BASE = "https://engineering.case.edu/sites/default/files/{id}.mat"

# local name -> CWRU file id
STARTER = {
    "normal_1hp_98.mat": 98,       # Normal_1,    healthy baseline
    "OR007at6_1hp_131.mat": 131,   # OR007@6_1,   outer race
    "IR007_1hp_106.mat": 106,      # IR007_1,     inner race
    "B007_1hp_119.mat": 119,       # B007_1,      ball
}

# Same three faults at 0.014 and 0.021 in, all 1 hp. Used to test whether a
# rule fitted to the 0.007 in records survives a change of fault size - it
# does not, which is the point of having them.
SEVERITY = {
    "OR014at6_1_198.mat": 198,
    "OR021at6_1_235.mat": 235,
    "IR014_1_170.mat": 170,
    "IR021_1_210.mat": 210,
    "B014_1_186.mat": 186,
    "B021_1_223.mat": 223,
}

DATA = Path(__file__).parent.parent / "data"


def fetch(name: str, file_id: int, dest: Path, attempts: int = 4) -> None:
    """Download one record, skipping it if a plausible copy is already there."""
    out = dest / name
    if out.exists() and out.stat().st_size > 100_000:
        print(f"  have  {name}  ({out.stat().st_size:,} bytes)")
        return

    url = BASE.format(id=file_id)
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                body = r.read()
            break
        except Exception as exc:  # the host drops connections fairly often
            if attempt == attempts:
                raise
            print(f"  retry {name}  ({exc})")
    else:  # pragma: no cover
        return

    out.write_bytes(body)
    print(f"  got   {name}  ({len(body):,} bytes)")


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    print(f"into {DATA}")
    for name, file_id in {**STARTER, **SEVERITY}.items():
        fetch(name, file_id, DATA)
    print("\ndone - now run: python src/verify_data.py")
