# Report outline

Target: 8-12 pages, figures taking about half. Every number comes from
`FACTS.md`; nothing is stated that is not on that sheet.

Word budgets are guides, not rules. The argument matters more than the length.

---

## The through-line

The report has one argument, and every section is a step in it:

> A bearing fault's identity is carried by *how often* an impact recurs, at a
> frequency the bearing's geometry predicts. That rhythm is not visible where
> it is expected, and the quantities that do detect a fault cannot name one.
> Recovering the rhythm requires the envelope of a resonance band, and the
> choice of that band has to be earned rather than assumed. What survives a
> change of fault size is the measurement, not anything learnt from the data.

Each section should end where the next one begins. A reader who skims the
section headings should still follow the argument.

---

## Abstract (~150 words)

What was done, on what data, what was found, and what failed. State the
headline numbers: envelope-spectrum peak-to-background ratios of 635 (outer
race) and 237 (inner race) against a healthy-record floor of 9.7; one false
positive in nine fault records; classifier accuracy falling from 96.3 percent
to 33.1 percent when the held-out fault diameter is unseen, against a 33.3
percent chance level.

Name the ball fault as undiagnosed here. An abstract that reports only
successes invites the reader to look for what was hidden.

---

## 1. Motivation (~250 words)

Write the true version. During a robotics internship, working on joint
teach-and-playback, it became clear that handling sensor signals was a gap:
there is no Signals and Systems course in the curriculum. This project was
done alongside self-study to close it, on a public dataset, with no hardware.

Say plainly what was chosen and why: a benchmark dataset so results can be
checked against published work, a fault type whose frequencies follow from
geometry so that predictions exist to test against, and a scope that ends at
a defensible decision rule rather than at a leaderboard number.

Two or three sentences of bearing-diagnosis background, cited. No literature
survey - this is not a review.

---

## 2. Data (~400 words + table)

- Source, bearing type, how the faults were made, the four loads.
- The table of records used: `FACTS.md` section 1.
- The fault-frequency multipliers and their source, with the arithmetic shown
  once for BPFO at 1772 rpm. This is the only equation the reader must follow.
- **The three data defects**, `FACTS.md` section 1. Give each two or three
  sentences: what it was, how it was established, what it would have cost.

State that the acceleration is treated as being in g by convention and that
the source does not label the unit, and note that the analysis depends on
frequencies and on ratios, both unaffected by that.

> This section is where a careful reader decides whether to trust the rest.
> The defects belong here, not in Limitations: finding them is work, and
> section 1 of `FACTS.md` is evidence that the data was checked rather than
> consumed.

---

## 3. Method (~900 words)

### 3.1 Why the fault frequency is where it is

Geometry to rhythm, in one short derivation. BPFO = 3.5848 x n.

### 3.2 Why a direct spectrum does not find it

An impact lasting under a millisecond is broadband; its energy goes to the
structural resonance it excites, not to the rate at which it recurs. Support
with the energy table (`FACTS.md` section 3): 97.4 percent of the outer-race
record's energy in 2000-4000 Hz, 0.2 percent below 500 Hz.

### 3.3 Envelope analysis

Band-pass, Hilbert envelope, transform. Explain the analytic signal in two
sentences and why the band-pass has to come first. Note removing the
envelope's mean and what happens if it is not removed.

### 3.4 Choosing the resonance band

This subsection carries the most weight in the report.

- The circularity: scoring a band by the peak at the fault frequency requires
  knowing the fault.
- What is genuinely known beforehand - geometry and speed, hence all three
  candidate frequencies - and what is not.
- The comb score, and why a geometric mean rather than an arithmetic one.
- Why not kurtosis: the retention table, and the `filtfilt` transient.
- The threshold, calibrated on the healthy record **over the same search**,
  with the selection-bias argument: 3.57 median against 11.06 after searching.

### 3.5 Classification

Features, both families. Peak ratios rather than energy shares, with the
reason. Segmentation without overlap. The four splits and what each asks.

---

## 4. Results (~1000 words, figures 1-7c)

One subsection per stage. Each figure gets two or three sentences: what it
shows, what the number is, what it rules out.

| subsection | figures | the point |
|---|---|---|
| 4.1 Time domain | 1, 2 + table 1 | ~21 bursts against BPFO x 0.2 s = 21.2; healthy kurtosis 2.98 against the Gaussian 3; ball fault invisible to two statistics of three |
| 4.2 Raw spectrum | 3a, 3b | energy at 2-4 kHz, not at the fault frequency; the BPFI peak present in the healthy record too |
| 4.3 Time-frequency | 4a, 4b, 4c | periodic striping; the band energy as a time series, which is the envelope in crude form; 601 at BPFO; the ball fault's band is bright but unmodulated |
| 4.4 Envelope spectrum | 5a, 5b | 635 and 237, errors under 0.5 percent, five harmonics; healthy floor 4.3 / 9.7 / 2.2 |
| 4.5 Band selection | 6a, 6b, 6c | comb against kurtosis; threshold 11.06; six race faults correct across fault size; **one false positive** |
| 4.6 Classification | 7a, 7b, 7c | 97.0 / 96.3 / 96.5 / 33.1; outer-race recall 0 percent on an unseen diameter |

**Section 4.5 must state the false positive in its own sentence, not in a
footnote.** Ball 0.021 in, 1.3x threshold, called inner race. Then the
three-tier rule and the observation that every error sits in the tier that
declines to be certain.

---

## 5. Discussion and limitations (~700 words)

### 5.1 What the results mean

The two methods fail differently, and the difference is the report's
conclusion. The rule from section 3.4 is a measurement of a quantity geometry
predicts; the classifier learns a map from waveform to label. Across an unseen
fault diameter the first holds and the second returns to chance. Time-domain
statistics reaching 33.1 percent against a 33.3 percent baseline is the
sharpest single result in the report - not a weak effect, no effect.

### 5.2 Limitations

Write at least these, each in a sentence or two:

1. One public dataset, one bearing type, one test rig. Laboratory data is far
   cleaner than a plant floor.
2. Faults are single points cut by EDM, not the spalling that real bearings
   develop.
3. The ball fault is not diagnosed at any diameter. Its band is energetic but
   unmodulated - detection without diagnosis.
4. One false positive in nine, and the threshold cannot separate it from the
   only marginally correct record.
5. The classifier was not tested across speed regimes far from these four, nor
   on a different machine.
6. The comb score's harmonic count and the band grid were fixed by hand; only
   the coarse-versus-fine grid check was done.
7. The segment length used throughout is best on neither split - 1024 samples
   generalises better, 4096 scores higher within a split.

> Every one of these is a finding, not an apology. Each says something specific
> about where the boundary of the result lies. A limitations section made of
> vague hedges says the author does not know where that boundary is.

### 5.3 What would come next

Two or three concrete items: testing the rule on a second dataset, cyclostationary
methods for the ball fault, and calibrating the threshold per machine from a
healthy baseline recorded on that machine.

---

## 6. What I learned (~400 words)

Half a page, honest, first person. The strongest material is the mistakes,
because each has a general lesson attached:

- A figure whose axes were four times wrong and looked fine - the baseline
  sampling rate.
- A duplicate record hidden inside another file, which would have leaked
  across a train/test split.
- Reaching for a standard criterion (kurtosis) and finding it selecting a
  filter artefact.
- Aligning a theoretical comb from t = 0 and concluding the theory was wrong,
  when only the phase was unknowable.
- Discovering that grouping by file, the usual advice, did not close the leak
  that mattered.

The common thread: every one of these was found by comparing against something
independent - a healthy record, a known-rate file, a synthetic signal with a
known answer, a second fault size. None of them raised an error.

---

## Appendix

- Repository link, with a one-line description of the layout.
- `src/verify_data.py` output, showing what is asserted about the data.
- Environment: Python version and library versions.

---

## If the page count runs over

Fifteen figures is a lot for twelve pages. Cut in this order, and no further:

1. **fig04b** - the band energy against time. It is the clearest single picture
   of the carrier-and-modulation idea, but fig04a already shows the rhythm and
   fig04c already shows its spectrum, so it is the one redundancy.
2. **fig03a** - the full spectra. Its content survives as the energy table.
3. **fig07c** - the feature space. It explains *why* the classifier fails,
   which is valuable, but fig07b already establishes *that* it does.

Never cut fig05b, fig06a, fig06c or fig07b. Those four carry the argument:
the diagnosis works, the band choice is earned, it survives a change of fault
size, and the classifier's accuracy depends on the split.

---

## Figure preparation

- Titles and axis labels in the figures are already English; no CJK glyphs, so
  no missing-font boxes.
- Figures are 150 dpi PNG. If the report is built in LaTeX, regenerate as PDF
  by changing the `savefig` extension - vector output prints sharper.
- Number the figures in the report in reading order, not by notebook. The
  current filenames carry the notebook number so they can be traced back.
- Every figure needs a caption that states the conclusion, not the contents.
  "Envelope spectra of the four records" is a label; "The outer-race and
  inner-race faults each peak only at their own predicted frequency, while the
  healthy record's tallest line reaches a ratio of 9.7" is a caption.
