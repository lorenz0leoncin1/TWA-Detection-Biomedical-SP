"""Configuration parameters for TWA detection"""

# Preprocessing parameters
SAMPLING_FREQUENCY = 1000  # Hz
LOWPASS_CUTOFF = 60  # Hz
RR_STABILITY_THRESHOLD = 0.10  # 10% of mean RR

# T-wave windowing parameters (heart rate dependent)
T_WAVE_ONSET = {
    'fast': (0.0, 0.6, 0.060),      # RR < 0.6s: onset at 60ms
    'normal': (0.6, 1.1, 0.100),    # 0.6s <= RR <= 1.1s: onset at 100ms
    'slow': (1.1, float('inf'), 0.150)  # RR > 1.1s: onset at 150ms
}

T_WAVE_LENGTH_FORMULA = lambda rr: 0.44 * rr - 0.14  # seconds

# Synchronization parameters
SYNC_SEARCH_RANGE = 0.030  # ±30ms

# Respiratory filter parameters
RESPIRATORY_FILTER_LOW = 0.14  # cycles/beat
RESPIRATORY_FILTER_HIGH = 0.35  # cycles/beat

# Correlation Method parameters
MIN_ALTERNATING_BEATS = 7
TWA_MAGNITUDE_THRESHOLD = 550  # µV (from paper: 97th percentile of healthy subjects)

# Analysis parameters
N_BEATS_ANALYSIS = 128  # Number of consecutive beats to analyze