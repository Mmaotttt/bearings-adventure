# Bearing fault diagnosis from vibration spectra

Envelope analysis of the CWRU bearing dataset: locating outer-race, inner-race
and ball faults by the frequency at which a rolling element strikes the defect.

## Layout

    data/       CWRU .mat records, plus FILES.md - the manifest
    notebooks/  exploratory work, one notebook per stage
    figures/    exported PNGs for the report
    report/     FACTS.md - every number with its provenance
                OUTLINE.md - the report's structure
    src/        the functions the notebooks settle on
                  cwru_io.py   loading records, fault frequencies
                  envelope.py  envelope analysis, band selection
    report.pdf  the write-up (not written yet)

## Setup

    python -m pip install numpy scipy matplotlib scikit-learn jupyterlab

Check the data loads and every record lands on one sampling grid:

    python src/verify_data.py

## Data

Four 1 hp records to begin with - healthy, outer race, inner race, ball, all
0.007 in faults. See `data/FILES.md` for ids, conditions, sources, and the two
corrections the baseline file needs.

## Running the notebooks

Double-click `start_jupyter.bat`, or from a shell in this directory:

    python -m jupyter lab --IdentityProvider.token=bearing

Then open <http://localhost:8888/lab?token=bearing>. The command does not
return - it is a server, and the terminal stays occupied until you stop it.
