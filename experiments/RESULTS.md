# Dionaea — benchmark results

## Experimental setup

Synthetic binary event streams; 15 independent training seeds; 40 held-out seeds per regime; episodes not samples are the positives. Settings selected once on moderate-noise training scenarios and fixed thereafter.

**No external dataset used; no NAB score is claimed.**

Training and test seeds are disjoint. Lower cost is better, but the cost weights are a research choice.

## Selected parameters (trained on moderate noise only)

```json
{
  "single": {
    "window": 6,
    "count": 3,
    "alpha": 0.8,
    "threshold": 1.6,
    "cooldown": 6
  },
  "pair": {
    "window": 2,
    "count": 3,
    "alpha": 0.8,
    "threshold": 1.6,
    "cooldown": 6
  },
  "count": {
    "window": 4,
    "count": 4,
    "alpha": 0.8,
    "threshold": 1.6,
    "cooldown": 6
  },
  "leaky": {
    "window": 6,
    "count": 3,
    "alpha": 0.55,
    "threshold": 1.9,
    "cooldown": 6
  }
}
```

## Held-out results

### moderate / independent noise

| Detector | Recall | Precision | F1 | False alerts (mean) | Cost (mean ± SD) |
|---|---:|---:|---:|---:|---:|
| single | 1.000 | 0.183 | 0.308 | 22.62 | 45.51 ± 5.20 |
| pair | 1.000 | 0.396 | 0.565 | 7.85 | 16.02 ± 3.49 |
| count | 0.960 | 0.746 | 0.830 | 1.85 | 5.34 ± 2.23 |
| leaky | 0.945 | 0.780 | 0.844 | 1.52 | 5.02 ± 2.67 |

### sparse true events

| Detector | Recall | Precision | F1 | False alerts (mean) | Cost (mean ± SD) |
|---|---:|---:|---:|---:|---:|
| single | 0.990 | 0.202 | 0.335 | 19.82 | 40.41 ± 5.09 |
| pair | 0.815 | 0.485 | 0.603 | 4.47 | 13.42 ± 4.12 |
| count | 0.300 | 0.817 | 0.422 | 0.10 | 14.63 ± 3.82 |
| leaky | 0.260 | 0.750 | 0.371 | 0.07 | 15.34 ± 3.92 |

### high background noise

| Detector | Recall | Precision | F1 | False alerts (mean) | Cost (mean ± SD) |
|---|---:|---:|---:|---:|---:|
| single | 1.000 | 0.131 | 0.231 | 33.45 | 67.32 ± 4.98 |
| pair | 1.000 | 0.225 | 0.367 | 17.43 | 35.30 ± 4.42 |
| count | 0.965 | 0.604 | 0.738 | 3.35 | 8.19 ± 2.90 |
| leaky | 0.945 | 0.654 | 0.764 | 2.77 | 7.43 ± 3.47 |

### correlated noise bursts

| Detector | Recall | Precision | F1 | False alerts (mean) | Cost (mean ± SD) |
|---|---:|---:|---:|---:|---:|
| single | 1.000 | 0.181 | 0.306 | 22.90 | 46.05 ± 5.52 |
| pair | 1.000 | 0.310 | 0.471 | 11.60 | 23.62 ± 5.46 |
| count | 0.955 | 0.524 | 0.672 | 4.58 | 10.97 ± 3.55 |
| leaky | 0.920 | 0.562 | 0.691 | 3.92 | 10.38 ± 4.82 |

## What to investigate yourself

- Does the detector ranking reverse when anomalies have very low event probability?
- How do bursty false signals defeat algorithms that count nearby events?
- Change the penalty on false positives and re-tune; do the rankings change?
- Investigate whether increasing the cooldown changes the ranking.

## Honest limitations

This is an illustrative synthetic experiment, not a proof of general superiority. The parameters were chosen using simulated events; the evaluation costs are subjective. All detector designs are existing general ideas, not new CS inventions. No statistical significance test or real-world validation has been performed. The plant biology is an inspiration, not the implementation of a biological model.
