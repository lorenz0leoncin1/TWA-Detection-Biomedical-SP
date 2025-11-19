"""Utility functions for data loading, plotting, and saving results"""

import numpy as np
import matplotlib.pyplot as plt
import json
import wfdb

def load_ecg_data(filepath, channel=0):
    """
    Load ECG data from PhysioNet format
    
    Args:
        filepath: Path to WFDB record (without extension)
        channel: Channel number to load
    
    Returns:
        ecg: ECG signal
        fs: Sampling frequency
        metadata: Record metadata
    """
    record = wfdb.rdrecord(filepath)
    ecg = record.p_signal[:, channel]
    fs = record.fs
    
    metadata = {
        'sig_name': record.sig_name[channel],
        'units': record.units[channel],
        'n_sig': record.n_sig,
        'fs': fs,
        'n_samples': len(ecg)
    }
    
    return ecg, fs, metadata


def plot_results(ecg, results, preprocessing_results, save_path=None):
    """
    Create comprehensive visualization of TWA analysis
    
    Args:
        ecg: Original ECG signal
        results: Results from CorrelationMethod.analyze()
        preprocessing_results: Results from ECGPreprocessor.preprocess()
        save_path: Optional path to save figure
    """
    fig, axes = plt.subplots(4, 1, figsize=(14, 12))
    
    # Plot 1: Original ECG with R peaks
    ax = axes[0]
    ax.plot(ecg, 'b-', linewidth=0.5, label='ECG')
    r_peaks = preprocessing_results['r_peaks']
    ax.plot(r_peaks, ecg[r_peaks], 'ro', markersize=5, label='R peaks')
    ax.set_title('Original ECG Signal with Detected R Peaks', fontsize=12, fontweight='bold')
    ax.set_xlabel('Sample')
    ax.set_ylabel('Amplitude')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Filtered ECG with T-wave windows
    ax = axes[1]
    ecg_filtered = preprocessing_results['ecg_filtered']
    ax.plot(ecg_filtered, 'b-', linewidth=0.5)
    
    # Highlight T-wave windows
    for start, end in preprocessing_results['t_windows'][:20]:  # Show first 20
        ax.axvspan(start, end, alpha=0.2, color='yellow')
    
    ax.set_title('Filtered ECG with T-Wave Windows (first 20 beats)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Sample')
    ax.set_ylabel('Amplitude')
    ax.grid(True, alpha=0.3)
    
    # Plot 3: ACI values
    ax = axes[2]
    aci = results['aci']
    beat_numbers = np.arange(len(aci))
    
    # Color alternating beats
    alternans_mask = results['alternans_mask']
    ax.plot(beat_numbers[~alternans_mask], aci[~alternans_mask], 
            'o', color='gray', markersize=6, alpha=0.5, label='Normal beats')
    ax.plot(beat_numbers[alternans_mask], aci[alternans_mask], 
            'o', color='red', markersize=8, label='Alternating beats')
    ax.plot(beat_numbers, aci, 'b-', linewidth=1, alpha=0.3)
    
    ax.axhline(y=1, color='k', linestyle='--', linewidth=2, label='Reference (ACI=1)')
    ax.set_title('Alternans Correlation Index (ACI)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Beat Number')
    ax.set_ylabel('ACI')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Results summary
    ax = axes[3]
    ax.axis('off')
    
    summary_text = f"""
    TWA DETECTION RESULTS
    ═══════════════════════════════════════════
    
    Status: {'TWA DETECTED ✓' if results['twa_detected'] else 'No TWA detected'}
    
    TWA Amplitude:        {results['amplitude_uV']:.2f} µV
    TWA Duration:         {results['duration_beats']} beats
    TWA Magnitude:        {results['magnitude']:.2f} µV
    
    Threshold:            {config.TWA_MAGNITUDE_THRESHOLD} µV
    
    ═══════════════════════════════════════════
    
    RR Stability:         {'Stable ✓' if preprocessing_results['is_stable'] else 'Unstable ✗'}
    Number of Beats:      {len(r_peaks)}
    """
    
    ax.text(0.1, 0.5, summary_text, transform=ax.transAxes,
            fontsize=11, verticalalignment='center',
            fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    
    plt.show()


def save_results(results, preprocessing_results, output_path):
    """
    Save analysis results to JSON file
    
    Args:
        results: Results dictionary from CorrelationMethod
        preprocessing_results: Results from ECGPreprocessor
        output_path: Path to save JSON file
    """
    output_data = {
        'twa_analysis': {
            'twa_detected': bool(results['twa_detected']),
            'amplitude_uV': float(results['amplitude_uV']),
            'duration_beats': int(results['duration_beats']),
            'magnitude': float(results['magnitude']),
            'aci_values': results['aci'].tolist(),
            'alternans_mask': results['alternans_mask'].tolist()
        },
        'preprocessing': {
            'is_stable': bool(preprocessing_results['is_stable']),
            'n_beats': len(preprocessing_results['r_peaks']),
            'r_peaks': preprocessing_results['r_peaks'].tolist(),
            'mean_rr_ms': float(np.mean(preprocessing_results['rr_intervals']) / 
                              config.SAMPLING_FREQUENCY * 1000)
        },
        'parameters': {
            'sampling_frequency': config.SAMPLING_FREQUENCY,
            'n_beats_analyzed': config.N_BEATS_ANALYSIS,
            'magnitude_threshold': config.TWA_MAGNITUDE_THRESHOLD,
            'min_alternating_beats': config.MIN_ALTERNATING_BEATS
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Results saved to {output_path}")


def print_summary(results):
    """Print formatted summary of TWA analysis"""
    print("\n" + "="*50)
    print("T-WAVE ALTERNANS DETECTION RESULTS")
    print("="*50)
    print(f"TWA Detected:      {'YES ✓' if results['twa_detected'] else 'NO ✗'}")
    print(f"Amplitude:         {results['amplitude_uV']:.2f} µV")
    print(f"Duration:          {results['duration_beats']} beats")
    print(f"Magnitude:         {results['magnitude']:.2f} µV")
    print(f"Threshold:         {config.TWA_MAGNITUDE_THRESHOLD} µV")
    print("="*50 + "\n")
