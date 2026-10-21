# DIONAEA.

**A small, research-led Computer Science project inspired by the Venus flytrap and an in-person Biomimicry Trail at Oxford Botanic Garden.**

**Research question:** *Can short-term temporal evidence integration suppress false activations in noisy event streams, and what is lost in detection responsiveness?*

This is a **working, AI-assisted starter project**, intended to be studied, challenged and independently extended by a Year 12/13 student. It is not an original plant model or a claim to have invented anomaly detection. Scientific interpretation, synthetic experiments and author contributions are carefully separated.

## Quick start (Windows, macOS, Linux)

Requires **Python 3.10 or newer**, no external Python packages. On Windows, you can also double-click `start_windows.bat` (provided Python is installed).

```bash
python app.py
```

Open **http://127.0.0.1:8765** in your browser. Change noise, burstiness, memory window, threshold and random seed. Watch the alarm timeline and true-episode scores update. Use *Replay* to show time progressing; the algorithms cannot see future signals.

Then run:

```bash
python -m unittest discover -s tests -v
python -m dionaea.benchmark
```

The benchmark regenerates `experiments/RESULTS.md` and `experiments/benchmark_results.json` from deterministic seeds.

### Optional: your own recorded events

Prepare a CSV with `t,event,label` (see `docs/FIELD_STUDY.md`) and run:

```bash
python -m dionaea.field_data your_observations.csv
```

This records event-level evidence and pre-labelled true episodes without using model predictions to create truth labels.

## Contents

```text
app.py                      local HTTP server + JSON API
web/index.html              browser lab and methodology
web/style.css               original responsive lab design
web/main.js                 interactive event timeline

dionaea/model.py            seeded synthetic stream generator
dionaea/detectors.py        four causal, explainable algorithms
dionaea/evaluate.py         episode-level metrics
dionaea/benchmark.py        train / held-out test comparison
dionaea/field_data.py       evaluate independent CSV observations

tests/                      automated correctness tests
experiments/RESULTS.md      genuine reproducible simulated results
experiments/benchmark_results.json  structured version of those results

docs/RESEARCH.md            science, methodology, sources and caveats
docs/STUDENT_WORKBOOK.md    six-week programme + interview questions
docs/LAB_NOTEBOOK.md        ownership and experiment journal
docs/EXPLAINED_FROM_ZERO.md Year 12 mathematics + CS walkthrough
docs/FIELD_STUDY.md         simple independent data-collection method
```

## Mathematics

The leaky integrator is defined as:

```text
S_t = alpha * S_(t-1) + x_t
trigger when S_t >= threshold
```

`x_t` is binary. `alpha` is a retention coefficient in the interval [0,1), *not* a measured plant constant. Timed pair and sliding count offer other simple decision rules. All four detectors share the same alarm cooldown and see the same event sequence.

## Fair comparison and limitations

The preconfigured benchmark chooses settings on **15 training seeds** from a moderate-noise scenario. It freezes those settings and tests the four algorithms on **40 held-out seeds** across each of **four environments**, using an explicitly stated subjective cost formula. `experiments/RESULTS.md` reports *the actual outputs of the included code*; it is not a prestigious external leaderboard score. A less cautious baseline may detect more episodes while producing more false alerts. The algorithms are standard well-known approaches.

Read `docs/RESEARCH.md` and `docs/STUDENT_WORKBOOK.md` before publishing your own claims or discussing the project in applications. The biggest admissions value comes from understanding the mathematics, making an independent change, documenting experiments and discussing the **limitations**, not from copying the starter application.

## Suggested next step

Investigate whether the memory parameter should adapt to changes in background event rate. Write a prediction first, design an online-only estimator and compare against the fixed-parameter detectors on *unseen* seeds. Alternatively, choose the simpler false-positive-cost sensitivity experiment in the workbook.

## References

- Oxford Botanic Garden, *Biomimetics*. https://www.botanic-garden.ox.ac.uk/biomimetics-exploiting-plants-design-technology
- Hedrich (2023), *Demystifying the Venus flytrap action potential*. https://doi.org/10.1111/nph.19113
- Suda et al. (2020), *Calcium dynamics during trap closure visualized in transgenic Venus flytrap*. https://doi.org/10.1038/s41477-020-00773-1
- Oxford CS personal statements: https://www.cs.ox.ac.uk/admissions/undergraduate/how_to_apply/personal-statement.html
- Cambridge guidance: https://www.undergraduate.study.cam.ac.uk/apply/how/ucas-personal-statement
- UCAS 2026-onwards personal statement format: https://www.ucas.com/applying/applying-to-university/writing-your-personal-statement/how-to-write-your-personal-statement-for-2026-entry-onwards

## Academic honesty / ownership

Starter code and documentation were generated with AI assistance. Before describing this as **your project** in an application, understand how it works, validate the results, make and document meaningful independent contributions, and describe who did what accurately. Repositories may honestly say *'Initially scaffolded with AI assistance; experimental design and analysis by [name]'* **only when that latter clause becomes true**.

You should not claim that Oxford reviewed or endorsed this code, that the algorithms are new, or that the benchmarks involve physical Venus flytraps.

## Licence

The original project code and written instructions may be reused and modified for educational purposes. Third-party research linked above retains its authors' copyright.
