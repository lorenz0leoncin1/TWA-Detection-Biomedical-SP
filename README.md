# T-Wave Alternans (TWA) Detection

Implementation of the **Correlation Method** for detecting microvolt T-Wave Alternans in Holter ECG recordings, based on **Burattini et al. (1999)**.

## What is TWA?

T-Wave Alternans is a beat-to-beat alternation in T-wave morphology — a marker of myocardial electrical instability and predictor of Sudden Cardiac Death (SCD).

## Algorithm Pipeline

Following Burattini et al. (1999):

1. **Low-Pass Filter** (60 Hz cutoff)
2. **R-Peak Detection** (maximum derivative method)
3. **Validation** — RR stability ≤10%, sinus beat correlation >0.8
4. **Baseline Removal** — cubic spline interpolation of PR interval
5. **T-Wave Extraction** — heart rate-dependent windowing
6. **T-Wave Synchronization** — ±30ms cross-correlation alignment
7. **Respiratory Removal** — band-stop filter (0.14–0.35 cycles/beat)
8. **TWA Detection** — Alternans Correlation Index (ACI) and Magnitude

## Key Equations

**Alternans Correlation Index:**
$$ACI_j = \frac{\sum T_j(i) \cdot T_{mdn}(i)}{\sum T_{mdn}^2(i)}$$

**TWA Magnitude:**
$$MAG_{CM} = A_{CM} \times N_{CM}$$

**Threshold:** MAG > 550 μV → TWA Positive

## Results (MUSIC SCD Database)

**8 patients analyzed, 6 with valid windows:**

| Patient | Lead | Magnitude (μV) | Result |
|---------|------|----------------|--------|
| P0001 | — | — | Rejected (arrhythmia) |
| P0002 | Z | 2034 | POSITIVE |
| P0003 | — | — | Rejected (arrhythmia) |
| P0004 | X | 2354 | POSITIVE |
| P0005 | Y | 2982 | POSITIVE |
| P0006 | X | 1092 | POSITIVE |
| P0007 | X | 1326 | POSITIVE |
| P0008 | X | 2968 | POSITIVE |

**Summary:** Mean 2126 μV | Max 2982 μV | Positive 6/6 (100%)

## Data Source

- **Database:** [PhysioNet MUSIC Database](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/)
- Patients with Sudden Cardiac Death in Heart Failure

## Usage

```bash
pip install -r requirements.txt
jupyter notebook TWA_Project_final.ipynb
```

## Reference

Burattini, L., Zareba, W., & Moss, A. J. (1999). Correlation method for detection of transient T-wave alternans in digital Holter ECG recordings. *Annals of Noninvasive Electrocardiology*, 4(4), 416-426.
