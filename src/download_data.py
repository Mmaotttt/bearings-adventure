"""Fetch the CWRU records this project uses.

    python src/download_data.py            # everything in the catalogue
    python src/download_data.py --starter  # just the four 1 hp records

The .mat files are not kept in the repository - they are a few megabytes each
and belong to the Bearing Data Center, not to us. `src/dataset.py` says what
each one is; this script brings them back.

Ids come from the tables at
<https://engineering.case.edu/bearingdatacenter/download-data-file>.
"""

import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import dataset

URL = "https://engineering.case.edu/sites/default/files/{id}.mat"
DATA = Path(__file__).parent.parent / "data"

# The records notebooks 01-05 need. Everything else exists for step 07.
STARTER_CODES = ("normal", "OR007at6", "IR007", "B007")


def fetch(record, dest, attempts=4):
    """Download one record, skipping it if a plausible copy is already there."""
    out = dest / record.filename
    if out.exists() and out.stat().st_size > 100_000:
        return False

    url = URL.format(id=record.cwru_id)
    body = None
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                body = r.read()
            break
        except Exception as exc:          # the host drops connections often
            if attempt == attempts:
                raise RuntimeError(f"{record.filename}: {exc}") from exc
            print(f"    retry {attempt}  {record.filename}  ({exc})")
    out.write_bytes(body)
    print(f"  got   {record.filename:<26} {len(body):>10,} bytes")
    return True


if __name__ == "__main__":
    starter = "--starter" in sys.argv
    records = (dataset.catalogue(loads=(1,), codes=STARTER_CODES) if starter
               else dataset.catalogue())

    DATA.mkdir(exist_ok=True)
    print(f"{len(records)} records into {DATA}\n")

    got = sum(fetch(r, DATA) for r in records)
    print(f"\ndownloaded {got}, already had {len(records) - got}")
    print("now run: python src/verify_data.py")
