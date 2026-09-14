# Dataset manifest

All records: Case Western Reserve University Bearing Data Center, drive-end
accelerometer (`DE`), motor load 1 hp. Test bearing at the drive end is an
SKF 6205-2RS JEM deep-groove ball bearing. Faults are single points put in by
electro-discharge machining, 0.007 in diameter.

Source pages consulted 2026-09-14:
<https://engineering.case.edu/bearingdatacenter/download-data-file>,
<https://engineering.case.edu/bearingdatacenter/apparatus-and-procedures>,
<https://engineering.case.edu/bearingdatacenter/bearing-information>

| Local file | CWRU id | Condition | Table | Native fs | rpm | rpm source |
|---|---|---|---|---|---|---|
| `normal_1hp_98.mat` | 98 / `Normal_1` | healthy baseline | Normal Baseline Data | 48 kHz | 1772 | load table |
| `OR007at6_1hp_131.mat` | 131 / `OR007@6_1` | outer race, 0.007 in, fault centred @6:00 | 12k Drive End | 12 kHz | 1773 | `X131RPM` |
| `IR007_1hp_106.mat` | 106 / `IR007_1` | inner race, 0.007 in | 12k Drive End | 12 kHz | 1772 | `X106RPM` |
| `B007_1hp_119.mat` | 119 / `B007_1` | ball, 0.007 in | 12k Drive End | 12 kHz | 1772 | `X119RPM` |

Each record is about 10 s long. Files keep their CWRU id in the name because
the variables inside are prefixed with it (`X131_DE_time`), so the id is what
ties a plot back to the source.

## Two things about the baseline file

The documentation states 12 kHz for the general set and 48 kHz "for drive end
bearing faults", and says nothing about the baseline rate. It is 48 kHz, which
matters because reading it as 12 kHz puts its whole frequency axis out by a
factor of four. Two independent checks:

* Three machine lines sit at 145.7 / 159.5 / 189.1 Hz in the known-12 kHz
  fault records. In file 98 they appear at those same frequencies only when it
  is read as 48 kHz; read as 12 kHz they fall at a quarter of them.
* Duration: 483903 samples is 10.08 s at 48 kHz, matching the fault records'
  ~10.2 s. At 12 kHz it would be 40.3 s, unlike every other record.

`cwru_io.load_baseline` therefore decimates it by 4 onto the 12 kHz grid.

The baseline file also carries no `RPM` variable and no `BA` channel, unlike
the fault files; its speed is taken from the CWRU load table (0/1/2/3 hp ->
1797/1772/1750/1730 rpm).

## Fault frequencies at 1 hp

Multipliers of shaft rate n = rpm/60, from the CWRU bearing specification for
the 6205-2RS JEM drive-end bearing. At 1772 rpm, n = 29.53 Hz.

| | multiplier | Hz at 1772 rpm |
|---|---|---|
| BPFO, outer race | 3.5848 | 105.9 |
| BPFI, inner race | 5.4152 | 159.9 |
| BSF, ball | 4.7135 | 139.2 |
| FTF, cage | 0.39828 | 11.8 |

## Still to download, for step 07 only

The classifier needs 3 fault types x 3 diameters (0.007/0.014/0.021 in) x
4 loads, roughly 36 files from the 12k Drive End table, plus the four baseline
files. Not needed before then.
