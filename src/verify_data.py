"""Check every downloaded record before anything is built on it.

    python src/verify_data.py          # one line per record
    python src/verify_data.py --quiet  # only the checks

The assertions are the point. Each one is a mistake this project already made
once, turned into something that cannot happen silently again:

  * every record must land on the 12 kHz grid, because the baselines arrive at
    48 kHz and reading one as 12 kHz puts its whole frequency axis out by four;
  * every record must report a speed within a few percent of its load's
    nominal, because treating the speed as constant across loads shifts every
    fault frequency by several Hz;
  * every record must be roughly ten seconds, because a wrong sampling rate
    shows up in the duration first;
  * no two records may hold identical samples. File 99 carries a byte-for-byte
    copy of file 98's channel alongside its own, and reading the wrong one
    would put the same samples in the dataset twice under different labels -
    a leak that flatters any classifier trained on it.
"""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import cwru_io
import dataset

DATA = Path(__file__).parent.parent / "data"

DURATION_RANGE = (9.0, 11.0)      # seconds
RPM_TOLERANCE = 0.05              # fraction of the load's nominal speed

# File 97 runs 5.08 s where every other record runs about 10. This is listed
# as a known exception rather than folded into DURATION_RANGE, because a wide
# range would stop the check from catching the thing it exists to catch - a
# baseline read at the wrong sampling rate, which shows up as a duration four
# times too long. That 97 is genuinely 48 kHz was settled separately: six
# machine lines land where a known 12 kHz record puts them only under that
# reading.
SHORT_RECORDS = {97}


def present():
    """Catalogue entries whose file is actually on disk."""
    return [r for r in dataset.catalogue() if (DATA / r.filename).exists()]


def check(record):
    sig = record.load_signal(DATA)
    nominal = dataset.RPM_BY_LOAD[record.load]
    problems = []
    if sig.fs != cwru_io.FS:
        problems.append(f"fs {sig.fs} != {cwru_io.FS}")
    if (record.cwru_id not in SHORT_RECORDS
            and not DURATION_RANGE[0] <= sig.duration <= DURATION_RANGE[1]):
        problems.append(f"duration {sig.duration:.2f}s outside {DURATION_RANGE}")
    if abs(sig.rpm - nominal) / nominal > RPM_TOLERANCE:
        problems.append(f"rpm {sig.rpm:.0f} far from nominal {nominal}")
    return sig, problems


if __name__ == "__main__":
    quiet = "--quiet" in sys.argv
    records = present()
    missing = [r.filename for r in dataset.catalogue()
               if not (DATA / r.filename).exists()]

    print(f"{len(records)} of {len(dataset.catalogue())} catalogue records on disk")
    if missing:
        print(f"  missing {len(missing)} - run: python src/download_data.py")
    print()

    if not quiet:
        print(f"{'file':<26}{'variable':<15}{'s':>6}{'rpm':>6}"
              f"{'BPFO':>8}{'BPFI':>8}{'BSF':>8}   label")
        print("-" * 96)

    failures = []
    for r in records:
        sig, problems = check(r)
        if problems:
            failures.append((r.filename, problems))
        if not quiet:
            f = sig.fault_freqs()
            flag = "  <-- " + "; ".join(problems) if problems else ""
            print(f"{r.filename:<26}{sig.key:<15}{sig.duration:>6.2f}{sig.rpm:>6.0f}"
                  f"{f['BPFO']:>8.1f}{f['BPFI']:>8.1f}{f['BSF']:>8.1f}   "
                  f"{r.label}{flag}")

    print()
    if failures:
        for name, problems in failures:
            print(f"FAIL {name}: {'; '.join(problems)}")
        raise SystemExit(f"{len(failures)} record(s) failed")

    # No record may be a copy of another.
    seen, duplicates = {}, []
    for r in records:
        digest = hashlib.sha1(r.load_signal(DATA).x.tobytes()).hexdigest()
        if digest in seen:
            duplicates.append((seen[digest], r.filename))
        seen[digest] = r.filename
    if duplicates:
        for a, b in duplicates:
            print(f"DUPLICATE {a} and {b} hold identical samples")
        raise SystemExit(f"{len(duplicates)} duplicate record(s)")

    rates = {check(r)[0].fs for r in records}
    assert rates == {cwru_io.FS}, f"records are not on one grid: {rates}"
    print(f"all {len(records)} records on the {cwru_io.FS} Hz grid, "
          f"speeds consistent with their load, durations ~10 s, "
          f"no two holding the same samples.")
