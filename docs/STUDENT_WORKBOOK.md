# Student workbook - make this a genuine Year 12/13 supercurricular

The supplied code is a functional **AI-assisted starter implementation**, not evidence that you personally designed every component. Keep this file in your repository and record your real work. The academic value starts when you understand, question and extend it.

## Six-week plan (approximately 3–5 hours each week)

### Week 1 - Understand the phenomenon (3h)
- [ ] Revisit your original Biomimicry Trail leaflet and write three observations you remember genuinely noticing.
- [ ] Read the abstract and selected figures of Suda et al. (2020), then the accessible Hedrich (2023) review.
- [ ] Explain to someone the difference between 'plant memory' and computer RAM.
- [ ] Write 150 words on what this model deliberately leaves out.
- **Evidence:** own notes, annotated reading and a dated entry in `docs/LAB_NOTEBOOK.md`.

### Week 2 - Own the algorithms (4h)
- [ ] Work through six time steps of `S_t = alpha*S_(t-1) + x_t` by hand with alpha 0.8, starting at zero.
- [ ] Draw your own state-machine diagram for the timed-pair detector.
- [ ] Locate and explain `detect()` in `dionaea/detectors.py`; intentionally break a test, then restore it.
- [ ] Write one new unit test covering a tricky event boundary or cooldown reset.
- **Evidence:** derivation, diagram, explanatory commit, your own new test.

### Week 3 - Form a falsifiable hypothesis (3h)
- [ ] Write your expected winner on the four test regimes BEFORE inspecting new results.
- [ ] Run `python -m dionaea.benchmark` and read `experiments/RESULTS.md`.
- [ ] Explain the difference between recall and precision using a concrete false-alarm example.
- [ ] Explain why changing settings until they work on test seeds is cheating.
- **Evidence:** dated prediction and reflection explaining surprises.

### Week 4 - Independent extension (5h)
Choose **one**, don't add everything:
- [ ] A: Compare performance under different false-positive costs, with train-only retuning.
- [ ] B: Design and test a two-stage detector (pair followed by leaky evidence) and compare it fairly.
- [ ] C: Compare fixed vs adaptive windows using ONLY preceding events, never future information.
- [ ] D: Modify synthetic noise to include long clusters and test whether detector rankings change.
- **Evidence:** new code, test, graph, clear negative results where applicable.

### Week 5 - Reality check (4h)
- [ ] Record your own small binary event dataset, such as controlled tapping on a keyboard/desk at known intervals.
- [ ] Separately mark the periods you intentionally generated true tapping patterns.
- [ ] Write `t,event,label` CSV and run `python -m dionaea.field_data your_file.csv`.
- [ ] Compare this to simulated results and openly discuss what changed.
- **Evidence:** dataset, reproducible protocol and method for obtaining ground truth.

### Week 6 - Academic explanation (4h)
- [ ] Create a 2–3 page report in your own words: question, model, method, results, limitations, next question.
- [ ] Make one annotated graph from the actual results; say what the graph can and cannot establish.
- [ ] Practise the interview questions below *without reading a script*.
- [ ] Draft 3–5 sentences for UCAS explaining the interest and what you really did and learned.
- **Evidence:** report, notebook, documented individual contributions.

## Interview practice (be ready for these)

1. What is the difference between a finite-state machine and a leaky accumulator?
2. With alpha=0.8 and x=(1,0,1), what are the three scores starting from zero?
3. Can increasing the time window create MORE false positives? Give a counterexample.
4. Why does a system that almost never raises alarms have high precision but potentially low recall?
5. How might you tune settings without accidentally using your test data twice?
6. If events were independent, how could you estimate the probability of two random events within a five-step window?
7. How would your conclusions change if missing a genuine event cost 100 times as much as a false alarm?
8. Why is this a Computer Science investigation, rather than just biology?
9. Which assumptions in the synthetic data generator do you distrust most?
10. Which part did you build or modify yourself, and which part came from an AI-assisted starting point?

## UCAS 2026-onwards format - where this belongs

- **Question 1 (motivation):** The visit prompted curiosity about biological systems as information processors. One sentence is enough.
- **Question 2 (academic preparation):** A-level maths / relevant mathematical reasoning such as recurrence relations, probability and algorithm analysis where it genuinely connects to your studies.
- **Question 3 (outside class):** The research, model, own code modifications, experiments, failure, revised question. Usually the strongest location for the detailed project example.

The format has three questions, with 4,000 characters total, so this one project must not overwhelm the rest of the application. Reflections matter more than a long list of technical nouns.

### A conditional narrative scaffold (do not present unfinished work as completed)

> After attending the Biomimicry Trail at Oxford Botanic Garden during the St John's Inspire Summer School, I became curious about how the Venus flytrap responds to repeated stimuli. Reading about its short-lived electrical signalling led me to investigate temporal evidence accumulation in computer systems. [Describe your **actual** mathematical model or code contribution]. I tested this against [actual baselines] and found [real measured trade-off]. This prompted me to question [specific limitation you genuinely explored].

Replace each bracket only after completing the underlying activity. Prefer your own voice, not a copied polished paragraph.

## Recommended sources

- Oxford CS: https://www.cs.ox.ac.uk/admissions/undergraduate/how_to_apply/personal-statement.html
- Oxford CS selection criteria: https://www.cs.ox.ac.uk/admissions/undergraduate/why_oxford/what_tutors_look_for.html
- Cambridge: https://www.undergraduate.study.cam.ac.uk/apply/how/ucas-personal-statement
- UCAS 3-question format: https://www.ucas.com/applying/applying-to-university/writing-your-personal-statement/how-to-write-your-personal-statement-for-2026-entry-onwards
