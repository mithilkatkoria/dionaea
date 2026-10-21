# Optional, achievable Year 12 field study

Collect a simple event stream with **your own** human tapping patterns rather than claiming sophisticated physical biology instrumentation.

## Minimal method

1. Decide on fixed one-second intervals (e.g. 120 seconds). Choose an object that gives discrete signals: a keyboard key, computer mouse, or simple button, rather than a poorly calibrated accelerometer.
2. Define 2–3 pre-planned *true event windows* (e.g. 30–40, 70–80 and 100–110 seconds) when a partner or you deliberately tap repeatedly. The truth windows must be chosen BEFORE looking at algorithm alerts.
3. Outside the windows, arrange occasional random taps as interference; record an `event=1` for any interval containing a tap and zero otherwise.
4. Build `t,event,label` CSV, where label=1 for a pre-planned true window, including intervals where no event was detected.
5. Run: `python -m dionaea.field_data path/to/observations.csv`.
6. Ask whether the relative ranking is similar to synthetic results. It might not be! Report all failures.

CSV example (a tiny illustrative *synthetic* file, not real observations):

```csv
t,event,label
0,0,0
1,1,1
2,1,1
3,0,1
4,0,0
5,1,0
6,0,0
7,1,1
8,1,1
9,0,0
```

In real data, sample consistently. Missing an interval must not be silently treated as an ordinary zero observation unless that is your defined handling rule. Do not claim a clinical device, real robot sensor, or biological dataset was tested when it was not.
