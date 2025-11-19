"""Correlation Method for TWA detection"""

import numpy as np
from . import config

class CorrelationMethod:
    """Implements the Correlation Method for TWA detection"""
    
    def __init__(self, min_alternating_beats=config.MIN_ALTERNATING_BEATS):
        self.min_alternating_beats = min_alternating_beats
    
    def compute_aci(self, t_waves):
        """Compute Alternans Correlation Index (Equation 1)"""
        max_len = max(len(tw) for tw in t_waves)
        padded = [np.pad(tw, (0, max_len - len(tw)), 'constant') for tw in t_waves]
        
        t_median = np.median(padded, axis=0)
        auto_corr = np.correlate(t_median, t_median, mode='full')
        max_auto_corr = np.max(auto_corr)
        
        aci = []
        for tw in padded:
            cross_corr = np.correlate(tw, t_median, mode='full')
            max_cross_corr = np.max(cross_corr)
            aci_value = max_cross_corr / max_auto_corr if max_auto_corr > 0 else 0
            aci.append(aci_value)
        
        return np.array(aci), t_median
    
    def detect_alternans(self, aci):
        """Detect alternating pattern in ACI values"""
        n_beats = len(aci)
        alternans_mask = np.zeros(n_beats, dtype=bool)
        aci_centered = aci - 1.0
        
        consecutive_alternating = 0
        start_idx = 0
        
        for i in range(1, n_beats):
            if aci_centered[i] * aci_centered[i-1] < 0:
                consecutive_alternating += 1
                if consecutive_alternating == 1:
                    start_idx = i - 1
            else:
                if consecutive_alternating >= self.min_alternating_beats - 1:
                    alternans_mask[start_idx:i] = True
                consecutive_alternating = 0
        
        if consecutive_alternating >= self.min_alternating_beats - 1:
            alternans_mask[start_idx:] = True
        
        n_alternating = np.sum(alternans_mask)
        return alternans_mask, n_alternating
    
    def quantify_twa(self, t_waves, aci, alternans_mask, t_median):
        """Quantify TWA amplitude (Equation 5)"""
        sum_t_median = np.sum(np.abs(t_median))
        n_samples = len(t_median)
        
        amplitudes = []
        for i, (tw, aci_val, is_alt) in enumerate(zip(t_waves, aci, alternans_mask)):
            if is_alt:
                a_cm = 2 * np.abs(aci_val - 1) * sum_t_median / n_samples
                amplitudes.append(a_cm)
        
        if len(amplitudes) > 0:
            mean_amplitude = np.mean(amplitudes)
            duration = len(amplitudes)
            magnitude = mean_amplitude * duration
        else:
            mean_amplitude = 0
            duration = 0
            magnitude = 0
        
        return mean_amplitude, duration, magnitude
    
    def analyze(self, t_waves):
        """Complete TWA analysis"""
        aci, t_median = self.compute_aci(t_waves)
        alternans_mask, n_alternating = self.detect_alternans(aci)
        amplitude, duration, magnitude = self.quantify_twa(
            t_waves, aci, alternans_mask, t_median
        )
        
        twa_positive = magnitude > config.TWA_MAGNITUDE_THRESHOLD
        
        return {
            'twa_detected': twa_positive,
            'amplitude_uV': amplitude,
            'duration_beats': duration,
            'magnitude': magnitude,
            'aci': aci,
            'alternans_mask': alternans_mask,
            't_median': t_median
        }