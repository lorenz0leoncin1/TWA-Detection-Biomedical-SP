"""
T-Wave Alternans Detection Package
Based on Burattini et al., 1999
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .preprocessing import ECGPreprocessor
from .correlation_method import CorrelationMethod
from .utils import load_ecg_data, plot_results, save_results

__all__ = [
    'ECGPreprocessor',
    'CorrelationMethod',
    'load_ecg_data',
    'plot_results',
    'save_results'
]