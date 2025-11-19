"""ECG preprocessing module"""

import numpy as np
from scipy import signal
from scipy.interpolate import UnivariateSpline
from . import config

class ECGPreprocessor:
    """Handles all preprocessing steps before TWA detection"""
    
    def __init__(self, fs=config.SAMPLING_FREQUENCY):
        self.fs = fs
        
    def lowpass_filter(self, ecg, cutoff=config.LOWPASS_CUTOFF):
        """Low-pass filter to reduce noise"""
        nyq = 0.5 * self.fs
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(4, normal_cutoff, btype='low', analog=False)
        return signal.filtfilt(b, a, ecg)
    
    def detect_r_peaks(self, ecg):
        """Detect R peaks in ECG"""
        threshold = 0.5 * np.max(ecg)
        peaks, _ = signal.find_peaks(ecg, height=threshold, 
                                     distance=int(0.4*self.fs))
        return peaks
    
    def check_rr_stability(self, r_peaks):
        """Check if RR intervals are stable"""
        rr_intervals = np.diff(r_peaks)
        mean_rr = np.mean(rr_intervals)
        std_rr = np.std(rr_intervals)
        is_stable = (std_rr / mean_rr) < config.RR_STABILITY_THRESHOLD
        return is_stable, rr_intervals
    
    def baseline_removal(self, ecg, r_peaks):
        """Remove baseline wander using cubic spline"""
        fiducial_offset = int(0.12 * self.fs)
        fiducial_points = r_peaks - fiducial_offset
        fiducial_points = fiducial_points[fiducial_points > 0]
        
        baseline_values = ecg[fiducial_points]
        spline = UnivariateSpline(fiducial_points, baseline_values, k=3, s=None)
        baseline = spline(np.arange(len(ecg)))
        
        return ecg - baseline
    
    def extract_t_waves(self, ecg, r_peaks):
        """Extract T-wave windows based on heart rate"""
        t_waves = []
        t_windows = []
        
        for i in range(len(r_peaks) - 1):
            rr = (r_peaks[i+1] - r_peaks[i]) / self.fs
            
            # Determine window onset
            if rr < 0.6:
                won = int(0.060 * self.fs)
            elif rr <= 1.1:
                won = int(0.100 * self.fs)
            else:
                won = int(0.150 * self.fs)
            
            # Determine window length
            wl = int((0.44 * rr - 0.14) * self.fs)
            
            start = r_peaks[i] + won
            end = start + wl
            
            if end < len(ecg):
                t_waves.append(ecg[start:end])
                t_windows.append((start, end))
        
        return t_waves, t_windows
    
    def synchronize_t_waves(self, t_waves):
        """Synchronize T waves using cross-correlation"""
        max_len = max(len(tw) for tw in t_waves)
        padded = [np.pad(tw, (0, max_len - len(tw)), 'edge') for tw in t_waves]
        t_median = np.median(padded, axis=0)
        
        synchronized = []
        search_range = int(config.SYNC_SEARCH_RANGE * self.fs)
        
        for tw in t_waves:
            best_corr = -np.inf
            best_shift = 0
            
            for shift in range(-search_range, search_range + 1):
                if shift < 0:
                    tw_shifted = np.pad(tw, (-shift, 0), 'edge')[:-shift or None]
                elif shift > 0:
                    tw_shifted = np.pad(tw, (0, shift), 'edge')[shift:]
                else:
                    tw_shifted = tw
                
                if len(tw_shifted) == len(t_median):
                    corr = np.corrcoef(tw_shifted, t_median[:len(tw_shifted)])[0, 1]
                    if corr > best_corr:
                        best_corr = corr
                        best_shift = shift
            
            if best_shift < 0:
                tw_sync = np.pad(tw, (-best_shift, 0), 'edge')[:-best_shift or None]
            elif best_shift > 0:
                tw_sync = np.pad(tw, (0, best_shift), 'edge')[best_shift:]
            else:
                tw_sync = tw
            
            synchronized.append(tw_sync)
        
        return synchronized
    
    def remove_respiratory_modulation(self, t_waves):
        """Remove respiratory modulation using band-stop filter"""
        amplitudes = np.array([np.max(np.abs(tw)) for tw in t_waves])
        
        b, a = signal.butter(2, 
                           [config.RESPIRATORY_FILTER_LOW, 
                            config.RESPIRATORY_FILTER_HIGH], 
                           btype='bandstop', fs=1.0)
        
        filtered_amplitudes = signal.filtfilt(b, a, amplitudes)
        
        filtered_t_waves = []
        for i, tw in enumerate(t_waves):
            if amplitudes[i] > 0:
                scale = filtered_amplitudes[i] / amplitudes[i]
                filtered_t_waves.append(tw * scale)
            else:
                filtered_t_waves.append(tw)
        
        return filtered_t_waves
    
    def preprocess(self, ecg, n_beats=config.N_BEATS_ANALYSIS):
        """Complete preprocessing pipeline"""
        ecg_filtered = self.lowpass_filter(ecg)
        r_peaks = self.detect_r_peaks(ecg_filtered)
        
        if len(r_peaks) > n_beats:
            r_peaks = r_peaks[:n_beats]
        
        is_stable, rr_intervals = self.check_rr_stability(r_peaks)
        ecg_corrected = self.baseline_removal(ecg_filtered, r_peaks)
        t_waves, t_windows = self.extract_t_waves(ecg_corrected, r_peaks)
        t_waves_sync = self.synchronize_t_waves(t_waves)
        t_waves_final = self.remove_respiratory_modulation(t_waves_sync)
        
        return {
            'ecg_filtered': ecg_filtered,
            'ecg_corrected': ecg_corrected,
            'r_peaks': r_peaks,
            't_waves': t_waves_final,
            't_windows': t_windows,
            'is_stable': is_stable,
            'rr_intervals': rr_intervals
        }