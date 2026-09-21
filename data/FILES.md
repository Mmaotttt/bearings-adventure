# Dataset manifest

All records: Case Western Reserve University Bearing Data Center, drive-end
accelerometer (`DE`). The test bearing at the drive end is an SKF 6205-2RS JEM
deep-groove ball bearing. Faults are single points put in by electro-discharge
machining at 0.007, 0.014 and 0.021 in diameter.

Source pages consulted 2026-09-14:
<https://engineering.case.edu/bearingdatacenter/download-data-file>,
<https://engineering.case.edu/bearingdatacenter/apparatus-and-procedures>,
<https://engineering.case.edu/bearingdatacenter/bearing-information>

The full catalogue is `src/dataset.py`; `python src/download_data.py` fetches
all of it, and `--starter` fetches only the four records notebooks 01-05 need.

Local files are named `<code>_<load>hp_<cwru id>.mat`. Forty records in all:
a healthy baseline plus three fault locations at three fault diameters, each
at all four motor loads.

| code | location | diameter | which frequency |
|---|---|---|---|
| `normal` | healthy | - | - |
| `IR007` `IR014` `IR021` | inner race | 0.007 / 0.014 / 0.021 in | BPFI |
| `B007` `B014` `B021` | ball | 0.007 / 0.014 / 0.021 in | BSF |
| `OR007at6` `OR014at6` `OR021at6` | outer race, fault @6:00 | 0.007 / 0.014 / 0.021 in | BPFO |

| load | approx. rpm | example id |
|---|---|---|
| 0 hp | 1797 | `OR007at6_0hp_130.mat` |
| 1 hp | 1772 | `OR007at6_1hp_131.mat` |
| 2 hp | 1750 | `OR007at6_2hp_132.mat` |
| 3 hp | 1730 | `OR007at6_3hp_133.mat` |

The fault records report their own speed in an `RPM` variable; the baselines
do not, so their speed comes from the load table above.

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

## Fault severity series, 1 hp

The 1 hp records at the two larger machined diameters were added to test
whether the time-domain statistics of step 02 survive a change of fault size.
They do not.

Whole-record kurtosis (Pearson convention) over all ten records, sorted:

    22.08  inner 0.014      7.59  outer 0.007
    21.97  outer 0.021      5.54  inner 0.007
     9.41  ball  0.021      2.98  HEALTHY
     8.84  ball  0.014      2.96  ball  0.007
     7.67  inner 0.021      2.94  outer 0.014

The classes interleave completely. Outer race spans 2.94 to 21.97, inner race
5.54 to 22.08, ball 2.96 to 9.41. The outer-race 0.014 in record is the worst
case: kurtosis 2.94 against the healthy record's 2.98, and RMS 0.094 against
0.062 - a real fault that reads as healthy on two of the three statistics.

A threshold fitted to the 0.007 in records therefore does not survive a change
of fault size, let alone a change of machine. This is the evidence behind the
claim that time-domain statistics identify a condition by lookup rather than
by measurement.
