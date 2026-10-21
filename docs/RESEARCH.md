# Research foundation and scientific honesty

## Starting point: a real Oxford visit

This project was suggested after participating in the St John's Inspire summer-school Biomimicry Trail at the University of Oxford Botanic Garden. The participant has a physical trail leaflet containing seven stops: Venus flytrap (*Dionaea muscipula*), sunflower, bromeliads, pitcher plants (*Nepenthes*), sensitive plant (*Mimosa pudica*), giant waterlily (*Victoria cruziana*) and water lettuce (*Pistia stratiotes*).

The leaflet describes biological mechanisms being used to inspire engineering and technology. It is a source of **personal motivation**, not experimental evidence for the claims below. The specific short-term memory interpretation comes from further scientific reading. A statement should distinguish what was observed at Oxford from what was subsequently read and modelled.

## Primary and authoritative background reading

1. Oxford Botanic Garden, *Biomimetics: exploiting plants for design in technology*. https://www.botanic-garden.ox.ac.uk/biomimetics-exploiting-plants-design-technology
   - Context for the interdisciplinary plant-to-engineering approach; especially pitcher plants.
2. R. Hedrich (2023), *Demystifying the Venus flytrap action potential*, **New Phytologist**. https://doi.org/10.1111/nph.19113
   - Accessible scientific review. Describes trigger hairs, action potentials, short-lived memory (~20 s) and summation of calcium transients. Our model DOES NOT simulate calcium waves or 20 seconds of real time.
3. H. Suda et al. (2020), *Calcium dynamics during trap closure visualized in transgenic Venus flytrap*, **Nature Plants**, 6, 1219–1224. https://doi.org/10.1038/s41477-020-00773-1
   - Experimental study of calcium signalling during flytrap closure.
4. T. Rahman (2026), *Threshold decision-making in the Venus flytrap*, **Plant Science**, 365, 113010. https://doi.org/10.1016/j.plantsci.2026.113010
   - Secondary quantitative reinterpretation of published experimental work; not needed to understand the student project.
5. Numenta, *Numenta Anomaly Benchmark*, https://github.com/numenta/NAB
   - Example of time-series anomaly data and scoring frameworks. Our project does **not** download it, run NAB, implement its scoring, or claim NAB results.

## What is being abstracted?

The biological concept is **temporal integration**: multiple events separated by time can, in some conditions, be more meaningful together than alone. The code models a binary event stream and introduces 4 **algorithmic** decision rules:

- Single event: alarm whenever x_t = 1 (subject to cooldown).
- Timed pair: alarm when two events arrive within a chosen number of discrete steps.
- Sliding-window count: alarm when k events occur within the last w steps.
- Leaky accumulator: S_t = alpha * S_{t-1} + x_t; alarm if S_t >= threshold.

The `alpha` parameter in the leaky accumulator represents a fraction retained per time step, *not* a biological rate measured from Venus flytraps. The window is in **simulation steps**, not seconds. These algorithms are standard pre-existing ideas, not an original discovery, and the system is not an AI model or a biological twin.

## Why not use raw NAB data immediately?

NAB contains real-valued time series and benchmark-defined anomaly windows. Our algorithms accept pre-processed **binary event signals**, which requires a defensible preprocessing step (e.g. an event is detected if a physical threshold is exceeded). Arbitrarily converting real-valued NAB observations to binary events and using truth labels to choose the threshold would produce misleading comparisons. NAB itself specifies its own scoring system. We start with synthetic data with transparent known labels and provide a CSV route for honest collection of real sensor observations. Using NAB is an **optional future phase** after you define preprocessing independently and avoid evaluation leakage.

## Experimental design

- Single scenario, fixed seed: debugging and visual learning.
- Multiple independent synthetic scenarios: avoid cherry-picking a single lucky example.
- Separate training seeds 1000–1014 (parameter selection) from held-out test seeds 2000–2039.
- Settings tuned once against the moderate-noise regime and then held fixed for every test regime.
- Four regimes: moderate independent noise; sparse genuine events; high background noise; correlated noise bursts.
- All four methods see the same stream and use the same fixed alarm cooldown.
- Episodes have exact binary ground truth intervals that are **not** visible to the detectors.
- Each episode contributes at most one true positive. Every additional alarm is false, even if it occurs in an already detected episode.

### Defined loss function (chosen, not discovered)

`cost = 4 * missed_episodes + 2 * false_alarms + 0.03 * total_first_detection_delay`.

Lower cost is considered better **under this chosen model of consequences**. Somebody monitoring expensive hardware failures might care much more about missed episodes; a non-critical vibration alert might instead assign higher cost to false alerts. Changing the loss function may change which detector wins.

### Limitations worth discussing in interviews

- Synthetic binary signals are not representative of a specific real device.
- Correlated noise bursts expose a limitation of proximity-based evidence schemes.
- We have no statistical significance test; observed mean differences could be noisy.
- Fixed global settings may underperform when event rates change over time.
- Our scores depend on arbitrary episode labels, cooldown and chosen cost weights.
- Delay is reported only for detected episodes; recall must be considered alongside it.
- The leaky detector and sliding-count methods are established patterns; no novel algorithm is claimed.

## What would make this research *yours*?

Read the papers, check the mathematics, reproduce benchmark outputs, question the cost assumptions, formulate a hypothesis BEFORE changing code, perform a controlled modification, write your own interpretation and explain a failure mode. If you collect independent observations, document the sensor, sampling frequency, procedure, labels and any preprocessing applied.

**Avoid claiming:** you discovered an original algorithm; your system duplicates flytrap biology; Oxford endorsed the project; you alone implemented every line if an AI assistant generated the starter code; the published synthetic results prove real-world superiority.
