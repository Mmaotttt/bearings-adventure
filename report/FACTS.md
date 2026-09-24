# Fact sheet

Every number the report may state, with where it comes from. Nothing goes into
the report that is not on this sheet or recomputed from the notebooks.

Regenerate any figure or table by running the notebook named beside it.

## Two conventions that resolve apparent contradictions

**Precision.** Values are listed as the code produces them. **In the report's
prose, round to three significant figures** - 237, not 236.9; 432, not 431.90.
The generated `.txt` tables keep the fuller precision; that difference between
a table and a sentence is normal and needs no comment. Where this sheet shows
both forms of the same quantity, the three-figure form is the one to write.

**Record length.** Two conventions appear, deliberately:

| convention | used in | why |
|---|---|---|
| whole record, each its own length | sections 2, 7 | a per-record statistic needs no common length |
| truncated to 120976 samples | sections 3, 4, 5, 6 | spectra are compared across records, and frequency resolution is fs/N, so unequal N would mean unequal line spacing |

120976 samples is the shortest of the four 1 hp records used in those sections
(the healthy one), giving 10.081 s and a resolution of 0.0992 Hz for **all**
records in those sections, not only the healthy one.

This is why RMS appears twice with different values, and both are correct:

| | whole record | truncated to 120976 |
|---|---|---|
| Healthy | 0.0617 | 0.0617 |
| Outer race | **0.5919** | **0.5921** |
| Inner race | **0.2929** | **0.2928** |
| Ball | 0.1391 | 0.1391 |

The report should use the whole-record column in section 4.1 and the
truncated column wherever it appears beside a spectral quantity, and say once,
in the method, that spectra are computed on a common 120976-sample window.

---

## 1. Dataset

Case Western Reserve University Bearing Data Center, drive-end accelerometer
(`DE` channel). Test bearing SKF 6205-2RS JEM, deep-groove ball bearing.
Faults are single points introduced by electro-discharge machining at 0.007,
0.014 and 0.021 in diameter. Catalogue in `src/dataset.py`, fetched by
`src/download_data.py`, checked by `src/verify_data.py`.

| | |
|---|---|
| Records used | 40 |
| Structure | healthy + 3 fault locations x 3 diameters, each at 4 motor loads |
| Sampling rate | 12 kHz (fault records); 48 kHz for the baselines, decimated by 4 |
| Record length | ~10 s, except file 97 at 5.08 s |
| Motor loads | 0 / 1 / 2 / 3 hp at approximately 1797 / 1772 / 1750 / 1730 rpm |
| Segments for classification | 2048 samples (0.171 s), non-overlapping, 2331 rows |

2331 rather than 40 x 59 = 2360, because record lengths differ slightly:

| segments | records | total |
|---|---|---|
| 29 | 1 (`normal_0hp_97.mat`, the 5.08 s baseline) | 29 |
| 59 | 38 | 2242 |
| 60 | 1 (`IR007_3hp_108.mat`, 122917 samples) | 60 |

Net: 30 fewer from the short baseline, one more from the longest record.

### Fault frequency multipliers

From the CWRU bearing specification for the 6205-2RS JEM. Multiply by shaft
rate n = rpm / 60.

| | multiplier | Hz at 1772 rpm (n = 29.53 Hz) |
|---|---|---|
| BPFO, outer race | 3.5848 | 105.9 |
| BPFI, inner race | 5.4152 | 159.9 |
| BSF, ball | 4.7135 | 139.2 |
| FTF, cage | 0.39828 | 11.8 |

### Three defects found in the data

These were found by widening `src/verify_data.py` from four hardcoded files to
the whole catalogue. All three are now assertions.

**a. The baselines are sampled at 48 kHz, which the documentation does not
state.** The apparatus page gives 12 kHz generally and 48 kHz "for drive end
bearing faults", saying nothing about the baselines. Established from the data
instead: three machine lines at 145.7 / 159.5 / 189.1 Hz in the known-12 kHz
fault records appear at those same frequencies in a baseline only when it is
read as 48 kHz, and at a quarter of them when read as 12 kHz. Durations agree
too: 10.08 s against the fault records' ~10.2 s, where 12 kHz would give 40.3 s.
Reading a baseline at 12 kHz puts its entire frequency axis out by a factor of
four, silently.

**b. File 99 contains a byte-for-byte copy of file 98's channel.** It holds
`X099_DE_time` and also `X098_DE_time`, identical to file 98's to the last
sample. Selecting the first key alphabetically returns file 98's samples under
file 99's name - the same data in the dataset twice under two labels, which
would leak across any train/test split. The loader now prefers the variable
carrying the file's own id.

**c. File 97 is 5.08 s where every other record is about 10.** The rate is not
the problem: six machine lines land where a known 12 kHz record puts them only
under a 48 kHz reading, and nowhere near it at 24 or 12 kHz. It is simply a
shorter recording, recorded as a known exception rather than by widening the
duration check.

Two of the four baselines carry an `RPM` variable and two do not; none carries
the base-plate channel the fault records have.

---

## 2. Time domain (notebook 01, 02) - figures 1, 2; table 1

### Peak acceleration over the first 0.2 s, 1 hp, 0.007 in faults

| | peak (g) |
|---|---|
| Healthy | 0.21 |
| Outer race | 2.85 |
| Inner race | 1.53 |
| Ball | 0.44 |

In that 0.2 s the outer-race record shows about 21 impulse bursts. BPFO x 0.2 s
= 21.2. The rhythm is directly countable by eye in one of the four records and
in neither of the other two faults.

### Whole-record statistics, 1 hp, 0.007 in (table 1)

Kurtosis in the Pearson convention, where Gaussian noise gives 3.

| | RMS (g) | kurtosis | crest factor |
|---|---|---|---|
| Healthy | 0.0617 | 2.98 | 4.58 |
| Outer race | 0.5919 | 7.59 | 5.26 |
| Inner race | 0.2929 | 5.54 | 5.40 |
| Ball | 0.1391 | 2.96 | 4.74 |

The healthy record's 2.98 against the Gaussian 3.00 confirms that a sound
bearing's vibration carries no impulsive structure.

Over 2048-sample segments (59 per record) kurtosis ranges 2.81-3.37 for the
healthy record and 2.67-3.40 for the ball fault: completely overlapping. Two
of the three statistics therefore miss the ball fault entirely. Only RMS
separates it, and RMS needs a healthy baseline of the same machine to mean
anything.

### Across fault size, 1 hp - whole-record kurtosis, sorted

| | | | |
|---|---|---|---|
| 22.08 | inner 0.014 | 7.59 | outer 0.007 |
| 21.97 | outer 0.021 | 5.54 | inner 0.007 |
| 9.41 | ball 0.021 | **2.98** | **HEALTHY** |
| 8.84 | ball 0.014 | 2.96 | ball 0.007 |
| 7.67 | inner 0.021 | 2.94 | outer 0.014 |

Outer race spans 2.94 to 21.97, inner race 5.54 to 22.08, ball 2.96 to 9.41.
The classes interleave and the healthy record sits inside the range. Inner
0.014 and outer 0.021 differ by 0.5 percent at different fault locations. The
outer-race 0.014 in record reads 2.94 against the healthy 2.98 - a real fault
that looks healthy on two statistics of three.

---

## 3. Raw spectrum (notebook 03) - figures 3a, 3b; table 2

10.08 s at 12 kHz, Hann window, resolution 0.099 Hz.

### Share of spectral energy per band (%), 1 hp, 0.007 in

| | 0-500 Hz | 2000-4000 Hz |
|---|---|---|
| Healthy | 29.4 | 12.1 |
| Outer race | **0.2** | **97.4** |
| Inner race | 0.6 | 78.1 |
| Ball | 1.9 | 92.7 |

Relative to the healthy record, the outer-race record carries 1382 times the
energy in 3000-4000 Hz and 379 times in 2000-3000 Hz, but **0.5 times** in
0-500 Hz - less than the healthy record has, in the band where theory says the
fault frequency lies.

### Amplitude at the theoretical fault frequencies (g)

| | BPFO 105.9 | BPFI 159.9 | BSF 139.2 | record RMS |
|---|---|---|---|---|
| Healthy | 0.00062 | 0.0093 | 0.00010 | 0.0617 |
| Outer race | 0.00207 | 0.0131 | 0.00016 | 0.5921 |
| Inner race | 0.00057 | 0.0124 | 0.00066 | 0.2928 |
| Ball | 0.00051 | 0.0117 | 0.00052 | 0.1391 |

At BPFI all four records carry a comparable peak, the healthy one included:
the 159.5 Hz machine line happens to fall beside BPFI at 159.9 Hz. Reading the
inner-race spectrum alone would confirm an inner-race fault, and the same
reasoning applied to the healthy record would confirm one there too.

At BPFO the outer-race record does carry 3.3 times the healthy amplitude, but
0.00207 g against a record RMS of 0.5921 g is 0.35 percent - an order of
magnitude below the machine lines beside it, and invisible on a linear axis.

The strongest lines below 500 Hz are common to all four records: 360.0, 419.0,
159.5, 353.4 and 189.1 Hz. 360 Hz is the sixth harmonic of the 60 Hz supply.

---

## 4. Time-frequency (notebook 04) - figures 4a, 4b, 4c; table 3

STFT with a 64-sample Hann window and hop 8, giving a 1500 Hz frame rate and
a 187.5 Hz frequency resolution.

**The parameters cannot be copied from a tutorial.** The common 256-sample
window at 50 percent overlap leaves a hop of 128 and a frame rate of 93.8 Hz,
whose Nyquist limit is 46.9 Hz. BPFO at 105.9 Hz is then not merely blurred
but absent from the frequency axis - the first attempt raised an empty-slice
error rather than returning a low score. The window and hop have to be derived
from the rhythm being looked for.

### Peak-to-background ratio in the spectrum of the 2000-4000 Hz band energy

| record | BPFO | BPFI | BSF |
|---|---|---|---|
| Healthy | 3.6 | 7.2 | 2.3 |
| Outer race | **601.0** | 9.5 | 30.2 |
| Inner race | 3.3 | **221.8** | 3.6 |
| Ball | 10.7 | 10.5 | 2.3 |

Each record peaks on its own fault frequency and nowhere else. The healthy row
sets the false-alarm floor. Outer-race harmonics: 601, 504, 371, 325 at 1x to
4x BPFO.

The spectrogram shows why the ball fault fails where numbers alone do not: its
3000-3800 Hz band is clearly brighter than the healthy record's, but it does
not flicker. Raised amplitude is what detection needs; periodicity is what
diagnosis needs, and this fault has only the first.

---

## 5. Envelope spectrum (notebook 05) - figures 5a, 5b; table 4

Band-pass 2000-4000 Hz, 4th-order Butterworth, zero phase; Hilbert envelope;
mean removed; transform.

### Verification on a synthetic signal

Impacts every 1/105.9 s exciting a 3 kHz decaying resonance, buried under three
times as much noise - the physical model, so the answer is known by
construction. Direct FFT scores a peak ratio of 3.0 at 105.9 Hz; the envelope
spectrum scores 31.8, with the peak at 105.90 Hz.

### Result on the 1 hp, 0.007 in records

| record | frequency | ratio | measured | error |
|---|---|---|---|---|
| Outer race | BPFO 105.9 | **635** | 106.3 Hz | +0.4% |
| Inner race | BPFI 159.9 | **237** | 159.5 Hz | -0.25% |
| Ball | BSF 139.2 | 2.1 | - | - |
| Healthy | (floor) | 4.3 / 9.7 / 2.2 | - | - |

Outer-race harmonics at 1x to 5x BPFO are all strongly present. The inner-race
record scores 2.9 at BPFO and 4.1 at BSF against 237 at BPFI - the computed
value is 236.9; write 237.

Compare with the raw spectrum: at BPFI the healthy and inner-race records were
within 33 percent of each other; after band-passing they differ by a factor of
24, because the 159.5 Hz machine line is removed before the envelope is taken.

### A numerical coincidence that must be stated, not left for the reader

The inner-race envelope peak is measured at 159.5 Hz. The machine line
identified in section 3 - the one that makes the raw spectrum unreadable at
BPFI - is also at 159.5 Hz. They are not the same object, and a reader who
notices the repetition without being told will suspect contamination.

They cannot be the same. Measured: in the band-passed signal the largest
amplitude anywhere between 100 and 250 Hz is 2.5e-12, against 1.2e-02 in the
raw signal - the 2000-4000 Hz band-pass attenuates that line by a factor of
about 5e9 before the envelope is taken. What remains at 159.5 Hz in the
envelope spectrum is a rate of amplitude modulation, not a spectral line that
leaked through.

Say so explicitly in the report. The coincidence is close enough to look like
an error.

### Two measurements that do not match the textbook

Sidebands spaced at shaft rate are expected around BPFI, because an inner-race
fault rotates through the load zone, and not around BPFO, because an
outer-race fault is stationary. Measured: the inner race's +/-1 shaft-rate
pair is weak (8.8 and 12.7) while +/-2 is strong (98.7 and 50.8), and the
outer race carries shaft-rate sidebands it is not supposed to have (106.1 and
113.4). Reported as an unexplained observation.

Omitting the envelope's mean leaves a DC peak 2.3 times the BPFO peak - not
the catastrophe usually described, but enough to halve every real peak on an
autoscaled axis and to defeat any automatic peak search.

---

## 6. Resonance band selection (notebook 06) - figures 6a, 6b, 6c; table 5

### The procedure

The three candidate frequencies follow from the bearing's geometry and the
shaft speed, both known before any diagnosis; which one is faulted is not.
So every candidate band is scored on all three candidates and the best is
kept, which decides the band and the diagnosis together without using the
answer.

Score: the geometric mean of the peak ratios at 1x to 4x the candidate
frequency. A geometric mean requires every harmonic to be present, where an
arithmetic mean would let one tall line carry the score - and one tall line is
what section 3 showed can be a machine line.

Grid: 55 bands, widths 500 / 1000 / 2000 Hz, centres every 250 Hz from 250 to
5800 Hz.

### Why not kurtosis

The kurtogram's usual criterion, applied here, retains this fraction of the
best achievable peak ratio:

| | kurtosis | comb score |
|---|---|---|
| Outer race | 23.9% | **98.5%** |
| Inner race | 64.4% | **95.8%** |
| Ball | 26.9% | 33.8% |

Kurtosis measures impulsiveness, and impulses arise from sensor sparks, single
mechanical knocks and filter ringing as readily as from bearings. The comb
score additionally requires periodicity.

A concrete instance: before edge trimming, the kurtosis criterion selected
250-750 Hz for the outer race. Trimming 5 percent from each end moved the pick
to 4750-5750 Hz. The original selection had been `filtfilt`'s own start-up
transient, which does not raise an error and looks like a result.

### Threshold

The highest comb score the healthy record reaches over the same 55-band
search: **11.06**. Its median over single bands is 3.57 and its 90th
percentile 8.55. Taking a single-band figure as the threshold would ignore
that the maximum of many noisy numbers exceeds any one of them, and would
manufacture false positives.

### Result, 1 hp, 0.007 in

| record | band | comb | x threshold | call | truth |
|---|---|---|---|---|---|
| Healthy | 750-1250 | 11.06 | 1.0 | no call | healthy |
| Outer race | 2750-3750 | 431.90 | **39.1** | BPFO | BPFO |
| Inner race | 1250-2250 | 226.92 | **20.5** | BPFI | BPFI |
| Ball | 2500-3000 | 9.66 | 0.9 | no call | BSF |

### Across fault size, 1 hp - the honest result

| record | band | comb | x threshold | call | truth | |
|---|---|---|---|---|---|---|
| outer 0.007 | 2750-3750 | 431.90 | 39.1 | BPFO | BPFO | correct |
| outer 0.014 | 750-1750 | 12.86 | **1.2** | BPFO | BPFO | correct |
| outer 0.021 | 1250-2250 | 85.10 | 7.7 | BPFO | BPFO | correct |
| inner 0.007 | 1250-2250 | 226.92 | 20.5 | BPFI | BPFI | correct |
| inner 0.014 | 2500-3000 | 36.42 | 3.3 | BPFI | BPFI | correct |
| inner 0.021 | 2000-4000 | 69.37 | 6.3 | BPFI | BPFI | correct |
| ball 0.007 | 2500-3000 | 9.66 | 0.9 | - | BSF | declined |
| ball 0.014 | 750-1250 | 10.37 | 0.9 | - | BSF | declined |
| ball 0.021 | 3250-4250 | 14.52 | **1.3** | BPFI | BSF | **false** |

All six race faults are diagnosed correctly even though the selected band
moves with both fault location and fault size. One false positive in nine.

It cannot be removed by raising the threshold: the only barely-correct record
(outer 0.014 at 1.2x) and the false one (ball 0.021 at 1.3x) are not separable
by this score. Hence a three-tier rule:

| comb / threshold | verdict | on these records |
|---|---|---|
| > 5x | diagnosis | 4 records, **4 correct** |
| 1x to 5x | tentative, re-measure | 3 records, 2 correct 1 wrong |
| < 1x | no call | 2 records |

Every error falls in the tier that admits to being unsure.

### How unstable the grey tier is

The same nine records scored on the whole record instead of the common
120976-sample window - a difference of at most 2000 samples, under 2 percent:

| record | truncated | whole record | |
|---|---|---|---|
| outer 0.007 | 431.90 correct | 462.28 correct | |
| outer 0.014 | 12.86 correct | 13.52 correct | |
| outer 0.021 | 85.10 correct | 87.35 correct | |
| inner 0.007 | 226.92 correct | 224.33 correct | |
| inner 0.014 | 36.42 correct | 36.77 correct | |
| inner 0.021 | 69.37 correct | 70.51 correct | |
| ball 0.007 | 9.66 declined | 9.76 declined | |
| **ball 0.014** | **10.37 declined** | **11.28 false** | **verdict flips** |
| ball 0.021 | 14.52 false | 14.29 false | |

One record changes verdict, and it is the one nearest the 11.06 threshold.
Every record more than a few percent clear of the threshold keeps its verdict.

This is the strongest available evidence for the three-tier rule: in the
1x-to-5x tier the verdict is not stable against a two percent change in how
much data is used, so a single number there cannot be treated as a diagnosis.
Above 5x nothing moves.

Both columns are correct; the truncated column is the one quoted elsewhere in
this sheet, because sections 3 to 6 all use the common window.

### If one fixed band must be used

Geometric mean of the peak ratio over the six race records:

| band | geometric mean |
|---|---|
| **1000-3000** | **109.8** |
| 2000-3000 | 102.0 |
| 2000-4000 | 93.6 |
| 2750-3750 | 80.7 |
| 1250-2250 | 56.6 |

1000-3000 Hz is best on none of the six individually and poor on none. The
2000-4000 Hz band used through section 5 - chosen by eye from a figure - drops
to 5.9 on the outer-race 0.014 in record.

---

## 7. Classifier (notebook 07) - figures 7a, 7b, 7c; table 6

40 records, 2048-sample non-overlapping segments, 2331 rows, 9 features,
envelope band 1000-3000 Hz, RBF SVM (C = 10) on standardised features.

Features: RMS, kurtosis, crest factor (time); peak-to-background ratio at
BPFO, BPFI, BSF and their second harmonics (envelope). Peak ratios rather than
energy shares - across unseen fault diameters, ratios score 50.7 percent
against shares' 42.1, because a share's denominator is the segment's own
energy, which mostly encodes load and fault size.

### Accuracy by split

| split | time (3) | envelope (6) | all (9) |
|---|---|---|---|
| A random shuffle | 97.0% | 77.9% | 95.9% |
| B grouped by file | 96.3% | 76.1% | 93.5% |
| C leave one load out | 96.5% | 75.6% | 93.9% |
| D leave one fault size out | **33.1%** | 50.7% | 48.3% |

Split D tests the three fault classes only; chance is 33.3 percent. The
time-domain features score 33.1 - not weak, empty.

Grouping by file costs only 2.4 points, because holding out one record leaves
the same fault at the same diameter under three other loads in the training
set. The leak that matters is between conditions, not between segments.

### Split D by held-out diameter

| | 0.007 | 0.014 | 0.021 |
|---|---|---|---|
| time (3) | 33.3% | 29.8% | 36.3% |
| envelope (6) | 58.4% | 31.6% | 62.0% |
| all (9) | 65.4% | 30.8% | 48.7% |

The 0.014 in column is worst for every feature set; that group includes the
outer-race record whose kurtosis is below the healthy record's.

### Confusion, 0.021 in held out, all nine features

Overall 48.7 percent, carried entirely by one class:

| true | recall |
|---|---|
| outer | **0%** |
| inner | 100% |
| ball | 46.2% |

Accuracy alone conceals a model that identifies not one outer-race segment.
Under split B the overall figure is 93.5 percent with the main confusion
between outer race and ball.

### Segment length

| length | B grouped | D unseen size |
|---|---|---|
| 512 | 87.7% | 54.7% |
| 1024 | 91.5% | **60.6%** |
| 2048 | 93.5% | 48.3% |
| 4096 | **94.2%** | 47.3% |

The best segment length depends on which split is being optimised. 2048 was
used throughout and is best on neither.

### The classifier is not short of physics - it declines to use it

Worth stating, because the obvious reading of the result is wrong. The
classifier is not failing for want of physical information: six of its nine
features are the peak ratios at the three geometry-derived fault frequencies
and their second harmonics, which is precisely the quantity sections 5 and 6
are built on.

That information does work. Across an unseen fault diameter the envelope
features alone reach 50.7 percent where the time-domain features reach 33.1.
But nothing obliges the model to use it, and on the training set identifying
a record by its tight cluster is both easier and more accurate than comparing
three peak ratios. It takes the easier route, and the easier route is the one
that does not survive a new fault size.

The lesson is not "add physics to the features". The physics was in the
features. The lesson is that an objective which rewards fitting the training
set will prefer whatever fits it, and a feature's physical meaning gives it no
standing in that competition.

### Against the method that does not learn

On the same unseen diameters, the section 6 rule diagnoses all six race
records correctly, having never been trained. Learning a map from waveform to
label does not extrapolate to a fault that was not in the training set;
measuring a frequency that geometry predicts does.

---

## 8. Figure and table inventory

**Every figure placed in the report must be taken from `figures/` as it stands
now, not from any earlier copy.** `fig01_waveforms.png` was regenerated on
2026-09-24 after the committed version was found to have been saved while the
notebook's exercise parameter was still set: it showed 0.02 s under a title
and a body text claiming 0.2 s and about 21 impulse bursts. The corrected file
is 225,645 bytes; the broken one is 192,504. If a build embeds an image whose
bytes do not match the repository, it is stale.


| file | notebook | shows |
|---|---|---|
| `fig01_waveforms.png` | 01 | four time-domain waveforms, 0.2 s |
| `fig02_time_stats.png` | 02 | RMS / kurtosis / crest, per-segment spread |
| `fig03a_spectrum_full.png` | 03 | raw spectra 0-6000 Hz, log axis |
| `fig03b_spectrum_zoom.png` | 03 | 0-500 Hz with fault frequencies marked |
| `fig04a_spectrogram.png` | 04 | spectrograms, 0.1 s, periodic striping |
| `fig04b_band_energy.png` | 04 | 2-4 kHz band energy against time |
| `fig04c_band_energy_spectrum.png` | 04 | spectrum of that band energy |
| `fig05a_envelope_construction.png` | 05 | raw, band-passed, envelope |
| `fig05b_envelope_spectra.png` | 05 | envelope spectra, four records |
| `fig06a_band_map.png` | 06 | comb score over 55 candidate bands |
| `fig06b_criterion_comparison.png` | 06 | comb score against kurtosis |
| `fig06c_robustness.png` | 06 | across fault size |
| `fig07a_confusion.png` | 07 | confusion, split B and split D |
| `fig07b_accuracy_by_split.png` | 07 | accuracy, four splits |
| `fig07c_feature_space.png` | 07 | feature space, colour by class |
| `table01_time_stats.txt` | 02 | whole-record statistics |
| `table02_band_energy.txt` | 03 | energy share per band |
| `table03_stft_peak_ratios.txt` | 04 | peak ratios, STFT band energy |
| `table04_envelope_peak_ratios.txt` | 05 | peak ratios, envelope spectrum |
| `table05_band_selection.txt` | 06 | selected bands and verdicts |
| `table06_classifier.txt` | 07 | accuracy by split |

---

## 9. Appendix material

### 9.1 Repository

<https://github.com/Mmaotttt/bearings-adventure>

Public, default branch `main`. The records themselves are not in it; they are
fetched by `src/download_data.py` and catalogued in `src/dataset.py`, so the
repository is about five megabytes and anyone can reproduce every figure from
it.

Suggested one-line description of the layout:

> `data/` holds the CWRU records, which are fetched by `src/download_data.py`
> rather than committed; `src/` holds the loading, envelope-analysis and
> feature code; `notebooks/` works through the seven stages in order; and
> `figures/` holds every figure in this report, each regenerated by the
> notebook that produced it.

### 9.2 Data checks - actual output of `src/verify_data.py`

Run on 2026-09-21. Reproduce with `python src/verify_data.py`.

```
40 of 40 catalogue records on disk

file                      variable            s   rpm    BPFO    BPFI     BSF   label
------------------------------------------------------------------------------------------------
normal_0hp_97.mat         X097_DE_time     5.08  1796   107.3   162.1   141.1   healthy 0hp
normal_1hp_98.mat         X098_DE_time    10.08  1772   105.9   159.9   139.2   healthy 1hp
normal_2hp_99.mat         X099_DE_time    10.11  1750   104.6   157.9   137.5   healthy 2hp
normal_3hp_100.mat        X100_DE_time    10.12  1725   103.1   155.7   135.5   healthy 3hp
IR007_0hp_105.mat         X105_DE_time    10.11  1797   107.4   162.2   141.2   inner 0.007" 0hp
IR007_1hp_106.mat         X106_DE_time    10.17  1772   105.9   159.9   139.2   inner 0.007" 1hp
IR007_2hp_107.mat         X107_DE_time    10.18  1748   104.4   157.8   137.3   inner 0.007" 2hp
IR007_3hp_108.mat         X108_DE_time    10.24  1721   102.8   155.3   135.2   inner 0.007" 3hp
IR014_0hp_169.mat         X169_DE_time    10.15  1796   107.3   162.1   141.1   inner 0.014" 0hp
IR014_1hp_170.mat         X170_DE_time    10.15  1774   106.0   160.1   139.4   inner 0.014" 1hp
IR014_2hp_171.mat         X171_DE_time    10.15  1752   104.7   158.1   137.6   inner 0.014" 2hp
IR014_3hp_172.mat         X172_DE_time    10.14  1728   103.2   156.0   135.7   inner 0.014" 3hp
IR021_0hp_209.mat         X209_DE_time    10.18  1797   107.4   162.2   141.2   inner 0.021" 0hp
IR021_1hp_210.mat         X210_DE_time    10.13  1774   106.0   160.1   139.4   inner 0.021" 1hp
IR021_2hp_211.mat         X211_DE_time    10.15  1752   104.7   158.1   137.6   inner 0.021" 2hp
IR021_3hp_212.mat         X212_DE_time    10.17  1728   103.2   156.0   135.7   inner 0.021" 3hp
B007_0hp_118.mat          X118_DE_time    10.21  1796   107.3   162.1   141.1   ball 0.007" 0hp
B007_1hp_119.mat          X119_DE_time    10.12  1772   105.9   159.9   139.2   ball 0.007" 1hp
B007_2hp_120.mat          X120_DE_time    10.13  1748   104.4   157.8   137.3   ball 0.007" 2hp
B007_3hp_121.mat          X121_DE_time    10.13  1722   102.9   155.4   135.3   ball 0.007" 3hp
B014_0hp_185.mat          X185_DE_time    10.15  1796   107.3   162.1   141.1   ball 0.014" 0hp
B014_1hp_186.mat          X186_DE_time    10.18  1772   105.9   159.9   139.2   ball 0.014" 1hp
B014_2hp_187.mat          X187_DE_time    10.17  1749   104.5   157.9   137.4   ball 0.014" 2hp
B014_3hp_188.mat          X188_DE_time    10.18  1724   103.0   155.6   135.4   ball 0.014" 3hp
B021_0hp_222.mat          X222_DE_time    10.17  1796   107.3   162.1   141.1   ball 0.021" 0hp
B021_1hp_223.mat          X223_DE_time    10.14  1774   106.0   160.1   139.4   ball 0.021" 1hp
B021_2hp_224.mat          X224_DE_time    10.18  1754   104.8   158.3   137.8   ball 0.021" 2hp
B021_3hp_225.mat          X225_DE_time    10.18  1729   103.3   156.0   135.8   ball 0.021" 3hp
OR007at6_0hp_130.mat      X130_DE_time    10.17  1796   107.3   162.1   141.1   outer 0.007" 0hp
OR007at6_1hp_131.mat      X131_DE_time    10.20  1773   105.9   160.0   139.3   outer 0.007" 1hp
OR007at6_2hp_132.mat      X132_DE_time    10.12  1750   104.6   157.9   137.5   outer 0.007" 2hp
OR007at6_3hp_133.mat      X133_DE_time    10.21  1725   103.1   155.7   135.5   outer 0.007" 3hp
OR014at6_0hp_197.mat      X197_DE_time    10.15  1796   107.3   162.1   141.1   outer 0.014" 0hp
OR014at6_1hp_198.mat      X198_DE_time    10.18  1772   105.9   159.9   139.2   outer 0.014" 1hp
OR014at6_2hp_199.mat      X199_DE_time    10.15  1749   104.5   157.9   137.4   outer 0.014" 2hp
OR014at6_3hp_200.mat      X200_DE_time    10.17  1723   102.9   155.5   135.4   outer 0.014" 3hp
OR021at6_0hp_234.mat      X234_DE_time    10.20  1796   107.3   162.1   141.1   outer 0.021" 0hp
OR021at6_1hp_235.mat      X235_DE_time    10.17  1771   105.8   159.8   139.1   outer 0.021" 1hp
OR021at6_2hp_236.mat      X236_DE_time    10.19  1748   104.4   157.8   137.3   outer 0.021" 2hp
OR021at6_3hp_237.mat      X237_DE_time    10.17  1721   102.8   155.3   135.2   outer 0.021" 3hp

all 40 records on the 12000 Hz grid, speeds consistent with their load, durations ~10 s, no two holding the same samples.
```

The final line is the assertion set: one sampling grid, speeds consistent with
the nominal for each load, durations near ten seconds, and no two records
holding identical samples. The last of those exists because of defect (b) in
section 1.

For the report, the 40-row listing can be cut to the four baselines plus a
note, or reproduced in full - it is the direct evidence that the data was
checked rather than assumed.

### 9.3 Environment

| | |
|---|---|
| Python | 3.12.1 |
| numpy | 2.4.4 |
| scipy | 1.17.1 |
| matplotlib | 3.10.8 |
| scikit-learn | 1.8.0 |
| jupyterlab | 4.6.3 |
| platform | Windows 11, AMD64 |

### 9.4 References - bibliographic details verified

Checked against CrossRef on 2026-09-24. Authors, journal, volume, pages and
DOI below are confirmed and may be cited as written.

1. Randall, R. B., & Antoni, J. (2011). Rolling element bearing diagnostics -
   a tutorial. *Mechanical Systems and Signal Processing*, **25**(2), 485-520.
   doi:10.1016/j.ymssp.2010.07.017
   The standard tutorial on envelope analysis; cite for the carrier-and-
   modulation argument in section 3.

2. Antoni, J. (2007). Fast computation of the kurtogram for the detection of
   transient faults. *Mechanical Systems and Signal Processing*, **21**(1),
   108-124. doi:10.1016/j.ymssp.2005.12.002
   The kurtogram. Section 3.4 departs from it and should therefore cite it.

3. Smith, W. A., & Randall, R. B. (2015). Rolling element bearing diagnostics
   using the Case Western Reserve University data: a benchmark study.
   *Mechanical Systems and Signal Processing*, **64-65**, 100-131.
   doi:10.1016/j.ymssp.2015.04.021
   A published assessment of this exact dataset. See 9.5.

---

### 9.5 What the benchmark study says about these records

**Verification status, which decides how this may be written.**

| | status |
|---|---|
| Bibliographic details above | **verified** against CrossRef |
| The substance below | **superseded - the paper has since been read; see section 11** |
| Any direct quotation | transcribed from page images, not copy-paste; see 11.1 |

Attempted on 2026-09-24 and failed: ScienceDirect returned a bot-check page
rather than the PDF (the saved `init.htm` was that challenge page, containing
no article text), and ResearchGate returned 403.

**Two tables were then supplied - A4 and B4 - and they are the wrong ones.**
Both are captioned *12 k fan end*: `Table A4, 12 k fan end bearing fault
data` and `Table B4, 12 k fan end bearing fault analysis results`. Their data
set numbers run 270 to 318. This project uses the 12 k **drive end** set -
105-108, 118-121, 130-133, 169-172, 185-188, 197-200, 209-212, 222-225,
234-237 - which appears nowhere in them. Nothing in A4 or B4 can be cited in
support of any claim about the records used here.

**What is needed instead**, and all three are still outstanding:

| | why |
|---|---|
| the A-table captioned *12 k drive end bearing fault data* | to map data set numbers to conditions for our records |
| its B-table counterpart, *12 k drive end ... analysis results* | the kurtosis and diagnosis category per record |
| Section 6.2 | it defines Y1 / Y2 / P1 / P2 / N1 / N2; without it the categories cannot be read |

**One observation from the fan-end tables, which is suggestive and is not
evidence.** In B4 the inner-race and outer-race-centred blocks carry many Y
ratings, while the ball-fault block (sets 282-293) is dominated by P and N
with no Y in the first method's column. That is the same shape as this
project's own result - races diagnosed, ball faults not - but it is a
different bearing at a different measurement point, so it may be mentioned
only as a remark, never as support.

Routes still open for the paper: a university IP or VPN, the library's
interlibrary request, or emailing the authors, who are at the School of
Mechanical and Manufacturing Engineering, UNSW.

The substance, as reported by sources citing the study: Smith and Randall
applied three established diagnostic techniques to the whole CWRU dataset and
graded every record by how diagnosable it proved. Relatively few records gave
the classical characteristics of their stated fault type; several were
reported as difficult or not diagnosable by any technique applied, **the
0.014 in drive-end inner-race and outer-race records among them, along with
most of the ball-fault records**.

**Until the PDF is in hand, paraphrase and attribute - do not quote.** A
paraphrase that is slightly loose is a small error; a fabricated quotation is
a serious one, and a reader who checks will check the quotation first.

### 9.6 How this may be used, and how it may not

Three places in the report currently say, in effect, "I do not know why":

| section | the unexplained thing |
|---|---|
| 4.1 | outer race 0.014 in has kurtosis 2.94, below the healthy record's 2.98 |
| 4.5 | that record is only just correct, at 1.2x the threshold |
| 4.6 | the 0.014 in column is the worst for every feature set |

All three may become "this is a known property of the dataset, and the method
still gave the correct call here", with the citation attached.

**There is a second and larger use.** The ball fault is not diagnosed here at
any diameter, and that is reported as this project's clearest failure. If most
ball-fault records are not diagnosable by established techniques either, then
the failure is a property of the data rather than of the method. Say so, and
say that it does not make the method better - it makes the result *legible*,
which is what a limitation section is for.

**What must not be written.** Not "outperforms the published benchmark", and
nothing of that shape.

Section 4.5.1 establishes that in the 1x-to-5x tier a verdict does not survive
a two percent change in record length. The outer-race 0.014 in call sits at
1.2x - inside that tier. It is a correct call in the band the report itself
marks as unreliable. A reviewer who reaches 4.5.1 will see the contradiction,
and the whole report's credibility rests on exactly the kind of care that
claim would abandon.

Wording that is both true and stronger:

> This record is reported in the benchmark literature as difficult to diagnose
> by established techniques. The rule proposed here gives the correct fault
> location for it, but at 1.2x the decision threshold - inside the tier this
> work marks as tentative, and shown in 4.5.1 to be unstable against a two
> percent change in record length. It is therefore offered as a correct call
> within an interval the method declines to be confident about, not as
> evidence of improvement over published methods.

That paragraph demonstrates the judgement the report is trying to show. The
triumphant version demonstrates the opposite.

---

## 10. Decisions for the write-up

Settled 2026-09-24. These are not measurements; they are choices, recorded
here so both language versions make the same ones.

### 10.1 Author block

    Bearing fault diagnosis from vibration spectra
    Chengzhe KONG
    Wuhan University of Technology
    September 2026
    github.com/Mmaotttt/bearings-adventure

The passport reads `KONG CHENGZHE`. Given-name-first is the convention for
applications to European institutions, and the spelling is identical either
way, so both orders are acceptable - **the family name in capitals is the
small improvement**: `Chengzhe KONG` keeps the European order while leaving
no doubt which name is the surname, and a reader matching this against a
passport or an application form has nothing to guess.

`Wuhan University of Technology` is the institution's own English name; do
not translate it differently.

### 10.2 The internship, in section 1

**Settled 2026-09-25 against the certificate, after a conflict with a company
registry lookup. The certificate governs.**

| | |
|---|---|
| Employer of record | **武汉京天电器有限公司** |
| Dates | 13 July 2026 to 24 July 2026 |
| Duration | 12 calendar days, Monday to Friday twice: **two working weeks** |
| Department | Technical Department |
| Role | Robot test engineer |

#### What the conflict was, and why it is not a conflict

A registry lookup returned 武汉京天机器人有限公司 - "Wuhan Jingtian Robotics
Co., Ltd." - and a draft was written from it. The certificate says 电器
(electric), not 机器人 (robotics). Two different registered names cannot both
be the employer.

The certificate is unambiguous. It carries 武汉京天电器有限公司 in three
independent places: the filled-in body text, the signature line, and the red
company seal.

The reason for the apparent mismatch is that they are the same business under
two names. 武汉京天电器有限公司 was founded in 2010 and operates in robotics
under the brand 京天博特 / 京天机器人, at jingtianrobots.com: intelligent
robotics R&D and systems integration, supplying robotics laboratories to
Chinese universities. The registered name says "electric"; the business is
robotics. That also explains why the role on the certificate is robot test
engineer at a company whose name suggests electrical goods, and why the name
was remembered as the robotics one.

#### What to write

**Whatever appears in the report must be what a reviewer sees on the seal**,
because the certificate is submitted alongside. So the registered name leads,
and the brand follows to explain the role:

Chinese version:

> 武汉京天电器有限公司（机器人业务品牌「京天机器人」）

English version - keep the Chinese characters so the reviewer can match the
seal directly, and mark the English as a rendering rather than a registered
name, which has not been verified to exist:

> Wuhan Jingtian Electric Co., Ltd. (武汉京天电器有限公司), a robotics firm
> trading as Jingtian Robotics

**Do not write "Wuhan Jingtian Robotics Co., Ltd." in either version.** It is
a different registered entity from the one that sealed the document being
submitted, whatever the relationship between them.

#### The rest of the sentence

**Write the two weeks.** The instinct is to leave the duration out, and it is
the wrong instinct here. The claim this section makes is not "I did
substantial work" - it is "this is where the question came from", and two
weeks is ample for a question to arise. Omitting the duration invites a
reader who also holds the CV to assume more and then find less. A report whose
entire posture is precision cannot afford to be vague about its one
unverifiable sentence.

**The role is better material than the field.** "Robot test engineer" explains
by itself how one ends up in front of joint teach-and-playback and its sensor
signals; "a robotics internship" explains nothing.

Suggested shape, to be rewritten in the author's own words:

> During a two-week internship as a robot test engineer at Wuhan Jingtian
> Electric Co., Ltd. (武汉京天电器有限公司), a robotics firm trading as
> Jingtian Robotics, in July 2026, working on joint teach-and-playback, I
> found that I could not reason about the sensor signals involved. There is no
> Signals and Systems course in my curriculum. This project was done alongside
> self-study to close that gap.

### 10.3 Appendix B - trim the verification output

Keep the four baseline rows and the final assertion line; add one sentence
saying the full 40-row output is in the repository. The four baselines are
where all three data defects live, so the evidence is concentrated there and
the remaining 36 rows only repeat the confirmation. This recovers close to a
page.

### 10.4 Figure captions - no filenames

Drop the grey filename from each caption. Put one sentence before the figure
list instead:

> Figures are named `figXXy_*.png` in the repository, numbered by the stage
> that produced them.

Traceability is preserved and the captions stay clean.

### 10.5 Length - aim at fourteen pages, not twenty-one

The outline budgeted 8-12 and the draft reached 21. Page count is not the
target; what matters is that a reader knows what was found before page three.

**Reconciling this with keeping all fifteen figures, which came later.** The
two instructions pull against each other and the figures win: a figure that
carries an argument is not padding. At fifteen figures the draft runs 22
pages, and that is the honest consequence.

Recover pages from layout, not from content. Several figures are wide and
short - the statistics comparison, the accuracy-by-split bars, the confusion
matrices - and can be set at reduced height or paired two to a row without
losing anything. Prose can tighten. Deleting a figure cannot.

And the page count matters less than what a reader meets first. The abstract
and section 4.0 already carry the result and the external validation; someone
who reads two pages has the substance.

Where to recover it:

| | |
|---|---|
| Appendix B | 40 rows to 5, per 10.3 |
| Figures | **keep all 15** - see below |
| Method | keep near its 900-word budget; envelope theory needs two sentences, and the space belongs to section 3.4 |
| **Discussion** | **do not compress** - this is the section that distinguishes the work |

**On the figure count, reversing an earlier instruction.** An earlier version
of this sheet said to cut from fifteen figures to twelve, dropping fig04b,
then fig03a, then fig07c. That was a page-budget heuristic applied without
checking what each figure carries, and review was right to push back on it.
Each of the three is the only illustration of its own argument: fig04b is the
band energy as a time series, which is the carrier-and-modulation idea made
visible; fig03a is the only picture of the energy sitting where the fault
frequency is not; fig07c is the only explanation of why the classifier
collapses rather than merely that it does.

**Keep all fifteen.** A figure that carries an argument is not padding, and
cutting one to save a page trades the argument for the page. Recover length
from prose if it is needed.

### 10.6 Both language versions draw from this sheet

Changes go into this file first, and both drafts are updated from it. Not
"change the Chinese and tell the English".

Three of the ten queries that came back from drafting - the RMS pair, the 2331
segments, 237 against 236.9 - were all the same failure: one quantity written
down in two places, drifting apart. The remedy is one place, not more careful
copying. The same failure took down notebook 06 when six filenames were
written into a notebook as well as into the catalogue.

### 10.7 The superseded draft

`REPORT_zh_draft_v1_superseded.md` is kept rather than deleted. It was written
against the 2026-09-21 sheet and its numbers are stale, but it records the
inconsistencies that review found, which is part of how the report was built.
Its header says so. Do not quote from it.

---

## 11. The benchmark study, read

Smith & Randall (2015) was read on 2026-09-24 from the published PDF. The
12 k drive-end tables are **A2** (p. 126) and **B2** (p. 128); the tables
supplied earlier, A4 and B4, are the fan-end ones and are not relevant here.

### 11.1 How reliable each part of this is

The paper could not be copied as text, so it was read as page images and
transcribed by hand. That leaves two different confidence levels, and they
must be treated differently:

| | confidence | why |
|---|---|---|
| Table B2's kurtosis values | **high** | independently cross-checked, see 11.2 |
| Prose quotations | transcribed, unconfirmed | nothing checks them |

**Quotations below may be used as paraphrase with a page citation. Before any
of them is printed inside quotation marks, check it against the PDF.**

Pages 102-103 and 105-128 were read in full; 101 and 104 only skimmed;
Tables B3/B4 and the references were not opened. So this section is what the
paper says about the drive-end data, not everything it says.

### 11.2 An external check on this project's own numbers

Table B2 publishes a kurtosis for every record. This project computed the
same quantity independently, before the paper was available, and the values
were not known to whoever transcribed the table.

**All 36 drive-end fault records agree.**

| | |
|---|---|
| Median difference | **0.06 %** |
| Largest difference | **0.3 %** |
| Records outside 0.5 % | none |

Examples: record 198 reads 2.94 in both; 186 reads 8.84 in both; 223 reads
9.41 in both; 170 reads 22.08 here against 22.1 printed.

This runs both ways. It confirms the transcription - thirty-six values do not
agree by accident - and it confirms this project's loading, channel selection
and kurtosis convention against an external published source. **Worth stating
in the report: the pipeline is validated against the literature, not only
self-consistent.**

The four baselines differ by 0.8 to 3.1 percent, and are expected to: the
paper computes on the native 48 kHz signal, this project on the 12 kHz
decimation. The direction and size of that difference are consistent with the
resampling, not with an error.

### 11.3 The diagnosis categories - Table 4, p. 107

| | success | definition (transcribed) |
|---|---|---|
| Y1 | yes | clearly diagnosable, classic characteristics in both time and frequency domains |
| Y2 | yes | clearly diagnosable but non-classic in either or both domains |
| P1 | partial | probably diagnosable; discrete components at the expected fault frequencies but not dominant |
| P2 | partial | potentially diagnosable; smeared components appearing to coincide with the expected frequencies |
| N1 | no | not diagnosable for the specified fault, but other problems identifiable, e.g. looseness |
| N2 | no | not diagnosable and virtually indistinguishable from noise |

Each cell in Table B2 reads DE/FE/BA. Methods 2 and 3 were run only where
Method 1 scored P1 or below.

### 11.4 What the paper says about the records this project uses

Published grades for the 1 hp records analysed throughout:

| this project's record | set | kurtosis (both) | paper's grade, DE channel |
|---|---|---|---|
| inner 0.007 | 106 | 5.54 | Y2 |
| inner 0.014 | 170 | 22.1 | Y2 |
| inner 0.021 | 210 | 7.67 | Y1 |
| ball 0.007 | 119 | 2.96 | **N1 / N2 / N1** - and listed in Table 6 |
| ball 0.014 | 186 | 8.84 | P2 |
| ball 0.021 | 223 | 9.41 | Y2 |
| outer 0.007 | 131 | 7.60 | Y1 |
| **outer 0.014** | **198** | **2.94** | **P2 / N2 / N2** |
| outer 0.021 | 235 | 22.0 | Y2 |

### 11.5 The three places that said "unexplained"

**4.1, the kurtosis of 2.94.** Record 198's kurtosis is 2.94 in the paper too.
The paper attributes anomalies of this kind not to fault size or speed but to
the rig's assembly (p. 107, transcribed): the diagnosis outcomes seem to be
less a function of the fault size or speed and load, and more a function of
the assembly, which was presumably the same within a fault size and changed
when a new bearing was installed; the suspected mechanism is mechanical
looseness whose severity changed with each installation. It repeats the point
at p. 110 and p. 124.

So the anomaly stops being unexplained: it is a documented property of this
rig, and this project reproduced the number exactly.

**4.5, the outer-race 0.014 in call at 1.2x threshold.** The sentence reported
earlier does appear, on p. 110, but its scope is narrower than it looked - it
sits in the section on outer-race faults centred in the load zone, so "the
next four series" means records 197 to 200, which is exactly this project's
0.014 in outer-race group. The paper's own grade for 198 is P2 at best, on
the drive-end channel with Method 1, and N2 with Methods 2 and 3.

**The honest framing, which is also the stronger one:** two independent
marginal assessments agree that this record is hard. The benchmark grades it
potentially diagnosable at best; the rule proposed here returns the correct
fault location but at 1.2x its threshold, inside the tier 4.5.1 shows to be
unstable against a two percent change in record length. Neither is a
confident diagnosis, and they agree about that.

Still not to be written: anything of the shape "outperforms the published
benchmark". See 9.6.

**One inconsistency inside the paper, worth noting rather than resolving.**
The p. 110 text says data set 197 is the only 0.014 in case with a partial
diagnosis, while Table B2 also shows P2 for 198 and P1 for 199 on the
drive-end channel under Method 1. Report it as an observation if it comes up;
do not try to explain it.

**4.6, the 0.014 in column being worst for every feature set.** Same
explanation: assembly rather than fault size, per p. 107.

### 11.6 The ball fault - the failure is corroborated

This project does not diagnose the ball fault at any diameter. The paper
reaches the same place by different routes:

- **Table 5** lists records that give classical symptoms with at least one
  method. The ball column is empty for all three groups - 12 k drive end,
  48 k drive end and 12 k fan end. No ball fault anywhere earns a Y1.
- **Table 6** lists records not diagnosable by any applied method. For 12 k
  drive-end ball faults it includes **118 and 119**. Record 119 is this
  project's ball 0.007 in at 1 hp - the record the rule declined to call.
- p. 108, transcribed: the ball fault cases are certainly the most difficult
  to diagnose, with only a few showing the classic envelope-spectrum symptoms;
  the only sets diagnosable by direct envelope analysis of the raw signal are
  from the 0.021 in and 0.028 in faults.
- p. 115 and p. 119 repeat the finding for the 48 k drive-end and 12 k fan-end
  data.

**This is the single most useful thing the citation does for the report.** The
clearest negative result here - detection without diagnosis on the ball fault
- is a property of the data that three established techniques also failed to
overcome. It does not make the method better. It makes the failure legible,
which is what a limitations section is for.

Note the direction of agreement on record 119 specifically: the rule declined
to diagnose it, and the benchmark found it not diagnosable. A method that
refuses where the literature also fails is behaving correctly.

### 11.7 The data defects, against the paper

**(a) The 48 kHz baselines: confirmed.** Table A1's caption (p. 126) states
48 kHz for the normal baseline data, and section 3.2 (p. 103) groups the whole
dataset by sample rate. This project established the same thing from three
machine lines before the paper was available. Keep the derivation in the
report - it is how the fact was found - and cite the paper as confirmation.

**(b) File 99's duplicated channel: not in the paper.** Table 3, "Records
affected by data acquisition problems" (p. 106), lists corrupted, clipped and
duplicated records - including five where the drive-end and fan-end
measurements are identical up to a scale factor of about 1.0154 - but neither
98 nor 99 appears in it. State this factually: not listed in the benchmark
study's table of acquisition problems. Nothing stronger.

**An inference that does not hold, recorded so it is not made again.** The
paper prints 2.93 for both 98 and 99, which looks like evidence that it too
read the duplicated channel. It is not. Computed on the native 48 kHz signal,
file 99's genuine `X099_DE_time` gives 2.9251 and the duplicate
`X098_DE_time` gives 2.9306. Both round to 2.93, so the printed values cannot
distinguish which was read.

**(c) File 97's 5.08 s duration: not addressed** in the pages read.

### 11.8 Where this belongs in the report

| section | what changes |
|---|---|
| Abstract | add the external validation: all 36 kurtosis values agree with the published benchmark to within 0.3 percent |
| 2, Data | cite the paper as confirmation of the 48 kHz baselines; note 98/99 is not in its Table 3 |
| 4.1 | the 2.94 is reproduced exactly; the anomaly is assembly, per p. 107 |
| 4.5 | 197-200 not diagnosable by the benchmark's techniques; both assessments marginal and agreeing |
| 4.6 | same assembly explanation |
| 5.2, Limitations | the ball fault: Table 5 empty, Table 6 lists 119, the method declined on 119 |
| new, or in 4 | the 36-record cross-check as a validation of the pipeline |
