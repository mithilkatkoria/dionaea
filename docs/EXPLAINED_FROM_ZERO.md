# Dionaea explained from zero - the Computer Science you must understand

This guide assumes Year 12 mathematical and Python knowledge. It deliberately avoids graduate-level biology, machine learning or statistics.

## 1. What is an event stream?

Every time step we record either `0` (no event) or `1` (event). A simple example is:

| Time t | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| Event x | 1 | 0 | 1 | 1 | 0 | 0 |

These could be button taps, vibrations above a chosen threshold or another binary event. We are not detecting whether an event occurred: we already have those values. We are deciding whether their **pattern** deserves an alert.

## 2. Why not simply alarm whenever x = 1?

If events can be caused by noise, a detector that fires at every `1` makes lots of false alarms. It may still have excellent detection recall. A useful decision involves a trade-off between responsiveness and reliability.

## 3. Timed pairs and a finite-state machine

A pair detector has two conceptual states: WAITING (no recent event) and ARMED (one event recently observed). A valid second event triggers an alarm and returns to WAITING. If no second event arrives before the window expires, it returns to WAITING without an alarm.

**Question:** If the window is 3 steps and events arrive at t=2 and t=5, should an alarm trigger? **Answer:** yes, the difference is 3. At t=6 it would be too late.

This is called a state machine because the response to the same incoming event depends on the current state. It is a simple model of computation, not proof that a Venus flytrap contains a software-based finite-state machine.

## 4. A leaky accumulator: basic recurrence relations

We choose:

`S_t = 0.8 * S_(t-1) + x_t`

Start with `S_-1 = 0`. Without an alarm/reset yet, an example is:

| t | event x_t | calculation | S_t |
|---|---:|---|---:|
| 0 | 1 | 0.8 × 0 + 1 | 1.00 |
| 1 | 0 | 0.8 × 1 + 0 | 0.80 |
| 2 | 1 | 0.8 × 0.8 + 1 | 1.64 |

If the alarm threshold is `1.6`, the detector fires at t=2. **Our implementation then resets the accumulator to zero** so later events cannot count the same evidence repeatedly.

An important observation: increasing alpha increases memory, but also means false signals can accumulate for longer. You must not assume more memory is always better.

## 5. What makes the comparison fair?

- Four detectors must see the **exact same input sequence**.
- They must share relevant constraints, such as cooldown and the evaluation rules.
- If you use data to choose thresholds, you must not report that same data as an independent performance test.
- A seeded random generator makes a simulation **reproducible**.
- A repeated benchmark checks whether one observation was just lucky.

## 6. Precision, recall, false alarms and delay

Suppose there are two real episodes. Your system detects one, misses one, and produces two false alarms.

- True positives TP = 1
- False negatives FN = 1
- False positives FP = 2
- Precision = TP/(TP+FP) = 1/3 ≈ 33.3%
- Recall = TP/(TP+FN) = 1/2 = 50%

Precision asks *how many alarms were genuinely useful?* Recall asks *how many of the real episodes did we detect?*

**Latency** matters too: raising an alarm ten steps into an episode may be less useful than raising it one step in.

## 7. Computational complexity (extension for interview discussion)

For a stream of n events:

| Detector | Total processing time | Extra memory used |
|---|---|---|
| Single event | O(n) | O(1) |
| Timed pair | O(n) | O(1) |
| Sliding count | O(n) amortised | O(w) worst case |
| Leaky accumulator | O(n) | O(1) |

Here `w` is the look-back window. The sliding-count deque removes each timestamp at most once; hence the total time stays linear even if some time steps remove several entries. The full app also stores traces and alarms for **visualisation**, which uses extra O(n) memory; the online decision logic itself need not store the entire stream.

## 8. Try predicting before running

- With `x = [1,0,0,0,1]`, does a 3-step timed pair trigger? Why?
- Can a threshold so high that nothing triggers give great precision? What happens to recall?
- If background events become clustered, which detectors might make more mistakes?
- Does a fixed 6-step cooldown unfairly punish true episodes that begin close together?
- Could a system adapt `alpha` using only previous observations, or would it need future information?

If you can solve these independently and explain how a change of assumptions affects the answer, you are developing exactly the mathematical reasoning you want to showcase.

## 9. The four rules side by side

| Rule | What it remembers | Decision |
| --- | --- | --- |
| Single event | No evidence between steps | Alarm for an observed 1, unless cooling down |
| Timed pair | One recent event timestamp | Alarm for a second event at most w steps later |
| Sliding count | Recent event timestamps | Alarm when at least k retained events lie in [t-w, t] |
| Leaky evidence | One fading evidence value | Alarm when alpha times the previous state plus the current event reaches the threshold |

All methods clear their evidence after an alarm. All use the same cooldown in a fair comparison. Memory describes how evidence persists before a decision; cooldown describes how long the detector ignores input after an alarm. They are different ideas.

The worked website example uses window 3, count 3, alpha 0.8, threshold 1.6 and cooldown 0. With 1, 0, 1, the single-event, pair and leaky methods alarm at t = 2; the three-event count does not. With another 1 at t = 3, count now fires. Leaky evidence was cleared after its previous alarm, so its state at t = 3 is only 1.00.

## 10. What the actual results establish

The comparison first chooses settings on 15 training seeds. Those settings are frozen before evaluation on 40 different seeds in each of four synthetic environments. This is parameter selection for standard algorithms, not a machine-learning system or a physiological simulator.

In moderate independent noise:

| Detector | Recall | Mean false alarms per stream | Detected-only mean delay (steps) |
| --- | ---: | ---: | ---: |
| Single | 100.0% | 22.625 | 1.760 |
| Pair | 100.0% | 7.850 | 2.165 |
| Count | 96.0% | 1.850 | 5.904 |
| Leaky | 94.5% | 1.525 | 6.195 |

Delay here averages the per-stream mean delays over streams that have detections. It must not be used alone: missing every episode produces no useful latency measurement. This implementation reports precision zero when there are no alarms, as an explicit convention.

Memory-based rules suppress many false alerts in this setting, but introduce misses and delay. The sparse-event setting exposes the limitation: leaky recall is 26%, count recall is 30%, pair recall is 81.5% and single recall is 99%. A good conclusion explains both outcomes.

The chosen cost is 4*misses + 2*false alarms + 0.03*total first-detection delay. Leaky has the lowest mean cost in three environments; pair has the lowest in the sparse environment. These are rankings under those penalty weights and this synthetic generator. No significance test establishes that a small mean difference is reliable, and no real-world sensor superiority has been demonstrated.

## 11. A first independent contribution

1. Work the short trace by hand and explain every decision, including a reset and a window boundary.
2. Reproduce the unchanged benchmark before modifying it.
3. Write one hypothesis first, such as whether a larger false-alert penalty selects more cautious thresholds and lowers recall.
4. Make one controlled code change, explain it and test a boundary case. If tuning settings, tune on training streams only and reserve a fresh evaluation seed set before looking at its outputs.
5. Save commands, settings, commit, results, a failed prediction and your own interpretation in the journal. State exactly where assistance was used.

Published test seeds cease to be an untouched evaluation set if you use their performance to guide further tuning. Keep the original reports as a baseline. The independent contribution is the reasoning, controlled change and evidence you can explain, rather than just the fact that a website exists.
