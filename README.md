# T-Wave Alternans Detection using Correlation Method

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Implementation of the **Correlation Method** for detecting T-Wave Alternans (TWA) in ECG signals, based on the paper by Burattini et al. (1999).

> **Reference:** Burattini, L., Zareba, W., & Moss, A.J. (1999). *Correlation Method for Detection of Transient T-Wave Alternans in Digital Holter ECG Recordings.* Annals of Noninvasive Electrocardiology, 4(4), 416-424.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Algorithm Description](#algorithm-description)
- [Dataset](#dataset)
- [Usage Examples](#usage-examples)
- [Results](#results)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## 🔍 Overview

**T-Wave Alternans (TWA)** is a beat-to-beat variation in the amplitude or morphology of the T-wave in ECG signals. It's a marker of cardiac electrical instability and associated with increased risk of ventricular arrhythmias.

This project implements a **time-domain correlation method** capable of detecting both:
- **Stationary TWA** (sustained episodes)
- **Non-stationary TWA** (transient episodes as short as 7 beats)

### Why This Method?

Unlike frequency-domain methods (e.g., spectral analysis), the correlation method can:
- ✅ Detect transient TWA episodes
- ✅ Work with sinus rhythm ECGs (no pacing required)
- ✅ Quantify both amplitude and duration of TWA
- ✅ Handle RR variability in ambulatory recordings

---

## ✨ Features

- **Complete preprocessing pipeline:**
  - Low-pass filtering (60 Hz)
  - R-peak detection
  - RR stability checking
  - Baseline wander removal
  - Heart rate-dependent T-wave windowing
  - T-wave synchronization via cross-correlation
  - Respiratory modulation removal

- **Correlation Method implementation:**
  - Alternans Correlation Index (ACI) computation
  - Pattern detection for alternating beats
  - TWA quantification (amplitude, duration, magnitude)

- **Utilities:**
  - PhysioNet data loading
  - Comprehensive visualization
  - Results export (JSON format)
  - Batch processing support

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/twa-detection.git
cd twa-detection
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Requirements

```txt
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
wfdb>=4.0.0
pandas>=1.3.0
```

---

## 🎯 Quick Start

### Basic Usage

```python
from twa_detection import ECGPreprocessor, CorrelationMethod
from twa_detection.utils import load_ecg_data, plot_results

# Load ECG data
ecg, fs, metadata = load_ecg_data('data/raw/record_name', channel=0)

# Preprocessing
preprocessor = ECGPreprocessor(fs=fs)
prep_results = preprocessor.preprocess(ecg, n_beats=128)

# TWA Detection
cm = CorrelationMethod(min_alternating_beats=7)
twa_results = cm.analyze(prep_results['t_waves'])

# Visualize results
plot_results(ecg, twa_results, prep_results, save_path='results/analysis.png')

# Print summary
print(f"TWA Detected: {twa_results['twa_detected']}")
print(f"Amplitude: {twa_results['amplitude_uV']:.2f} µV")
print(f"Duration: {twa_results['duration_beats']} beats")
```

### Command-Line Interface

```bash
# Analyze a single ECG record
python scripts/run_analysis.py --input data/raw/record_001 --output results/

# Batch process multiple records
python scripts/batch_process.py --input-dir data/raw/ --output-dir results/
```

---

## 📁 Project Structure

```
twa-detection/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── setup.py                  # Package installation script
├── LICENSE                   # MIT License
├── .gitignore               # Git ignore rules
│
├── data/
│   ├── raw/                 # Raw ECG data from PhysioNet
│   └── processed/           # Processed results
│
├── src/
│   └── twa_detection/
│       ├── __init__.py      # Package initialization
│       ├── config.py        # Configuration parameters
│       ├── preprocessing.py # ECG preprocessing
│       ├── correlation_method.py  # Core algorithm
│       └── utils.py         # Utility functions
│
├── scripts/
│   ├── download_data.py     # Download MUSIC database
│   ├── run_analysis.py      # Single record analysis
│   └── batch_process.py     # Batch processing
│
├── tests/
│   ├── test_preprocessing.py
│   └── test_correlation_method.py
│
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   └── 02_results_visualization.ipynb
│
├── results/
│   ├── figures/             # Generated plots
│   └── metrics/             # Performance metrics
│
└── docs/
    ├── algorithm_description.md
    └── references.md
```

---

## 🧮 Algorithm Description

### Overview

The algorithm consists of two main stages:

#### **Stage 1: Preprocessing**

1. **Low-pass filtering** (60 Hz cutoff) to reduce noise
2. **R-peak detection** using derivative-based method
3. **RR stability check** (reject if std > 10% of mean)
4. **Baseline removal** using cubic spline interpolation
5. **T-wave windowing** (heart rate-dependent formulas):
   - Onset: 60ms (RR<0.6s), 100ms (0.6-1.1s), 150ms (RR>1.1s)
   - Length: `0.44×RR - 0.14` seconds
6. **T-wave synchronization** via cross-correlation (±30ms search)
7. **Respiratory modulation removal** (0.14-0.35 cycles/beat bandstop)

#### **Stage 2: Correlation Method**

1. **Compute median T-wave** from 128 consecutive beats
2. **Calculate ACI** (Alternans Correlation Index) for each beat:
   ```
   ACI_j = max(cross_corr(T_j, T_median)) / max(auto_corr(T_median))
   ```
3. **Detect alternating pattern**: ACI values oscillate around 1.0
4. **Quantify TWA**:
   - **Amplitude** (µV): `2 × |ACI_j - 1| × sum(T_median) / N_samples`
   - **Duration**: Number of alternating beats
   - **Magnitude**: Amplitude × Duration

#### **Detection Criteria**

- Minimum 7 consecutive alternating beats
- TWA magnitude > 550 µV (97th percentile of healthy subjects)

---

## 📊 Dataset

### MUSIC Database

**Recommended dataset:** [MUSIC - Sudden Cardiac Death in Chronic Heart Failure](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/)

- **Subjects:** 139 heart failure patients
- **Channels:** 2-lead Holter ECG (modified V3, V5)
- **Sampling rate:** 500 Hz
- **Duration:** ~5 hours per recording
- **Use case:** High risk of arrhythmias, ideal for TWA detection

### Download Data

```bash
# Using provided script
python scripts/download_data.py --output data/raw/ --n-records 10

# Manual download from PhysioNet
wget -r -N -c -np https://physionet.org/files/music-sudden-cardiac-death/1.0.1/
```

### Data Format

The project uses WFDB format (standard for PhysioNet):
- `.dat` - Binary signal data
- `.hea` - Header file with metadata
- `.atr` - Annotations (if available)

---

## 💡 Usage Examples

### Example 1: Analyze Single ECG Record

```python
from twa_detection import ECGPreprocessor, CorrelationMethod
from twa_detection.utils import load_ecg_data, save_results, print_summary

# Load data
ecg, fs, _ = load_ecg_data('data/raw/music_001', channel=0)

# Preprocess
preprocessor = ECGPreprocessor(fs=fs)
prep_results = preprocessor.preprocess(ecg)

# Detect TWA
cm = CorrelationMethod()
twa_results = cm.analyze(prep_results['t_waves'])

# Display results
print_summary(twa_results)

# Save results
save_results(twa_results, prep_results, 'results/music_001_results.json')
```

### Example 2: Custom Parameters

```python
from twa_detection import ECGPreprocessor, CorrelationMethod
from twa_detection import config

# Modify parameters
config.MIN_ALTERNATING_BEATS = 10  # Require 10 beats instead of 7
config.TWA_MAGNITUDE_THRESHOLD = 600  # Stricter threshold

# Run analysis with custom parameters
preprocessor = ECGPreprocessor(fs=1000)
cm = CorrelationMethod(min_alternating_beats=10)

# ... rest of analysis
```

### Example 3: Batch Processing

```python
import os
from pathlib import Path
from twa_detection import ECGPreprocessor, CorrelationMethod
from twa_detection.utils import load_ecg_data

data_dir = Path('data/raw')
results_dir = Path('results/batch')
results_dir.mkdir(exist_ok=True)

for ecg_file in data_dir.glob('*.hea'):
    record_name = ecg_file.stem
    
    try:
        ecg, fs, _ = load_ecg_data(str(data_dir / record_name))
        
        preprocessor = ECGPreprocessor(fs=fs)
        prep_results = preprocessor.preprocess(ecg)
        
        cm = CorrelationMethod()
        twa_results = cm.analyze(prep_results['t_waves'])
        
        # Save results
        output_file = results_dir / f"{record_name}_twa.json"
        save_results(twa_results, prep_results, str(output_file))
        
        print(f"✓ {record_name}: TWA={'Detected' if twa_results['twa_detected'] else 'Not detected'}")
        
    except Exception as e:
        print(f"✗ {record_name}: Error - {str(e)}")
```

---

## 📈 Results

### Performance Metrics

The algorithm performance should be evaluated on:

1. **Sensitivity**: True positive rate for TWA detection
2. **Specificity**: True negative rate (healthy subjects)
3. **Accuracy**: Overall correct classifications
4. **Quantification error**: Accuracy of amplitude/duration estimates

### Expected Results (from original paper)

- **Healthy subjects:** 97% negative (magnitude < 550 µV)
- **LQTS patients:** 44% TWA-positive, with 47% showing transient TWA
- **Quantification error:** Median 31% relative error in simulation

### Visualization

The `plot_results()` function generates:
- Original ECG with R-peak detection
- Filtered ECG with T-wave windows
- ACI plot showing alternating pattern
- Summary statistics

---

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_preprocessing.py

# Run with coverage
python -m pytest --cov=twa_detection tests/
```

### Test Structure

```
tests/
├── test_preprocessing.py    # Test ECG preprocessing steps
├── test_correlation_method.py  # Test TWA detection
└── test_utils.py            # Test utility functions
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Include type hints where appropriate
- Write unit tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Original paper authors:** Laura Burattini, Wojciech Zareba, Arthur J. Moss
- **PhysioNet:** For providing open-access physiological data
- **MUSIC Database contributors:** For the cardiac death dataset
- **Course instructors:** Roberto Sassi and Massimo Rivolta (University of Milan)

---

## 📞 Contact

**Project Maintainer:** Your Name  
**Email:** your.email@example.com  
**Course:** Biomedical Signal Processing  
**Institution:** University of Milan  

---

## 📚 References

1. Burattini, L., Zareba, W., & Moss, A.J. (1999). Correlation Method for Detection of Transient T-Wave Alternans in Digital Holter ECG Recordings. *Annals of Noninvasive Electrocardiology*, 4(4), 416-424.

2. Rosenbaum, D.S., et al. (1994). Electrical alternans and vulnerability to ventricular arrhythmias. *New England Journal of Medicine*, 330(4), 235-241.

3. Nearing, B.D., et al. (1991). Dynamic tracking of cardiac vulnerability by complex demodulation of the T wave. *Science*, 252(5004), 437-440.

---

## 📝 Citation

If you use this code in your research, please cite:

```bibtex
@misc{twa_detection_2024,
  author = {Your Name},
  title = {T-Wave Alternans Detection using Correlation Method},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/yourusername/twa-detection}
}
```

---

**Last Updated:** November 2024  
**Version:** 1.0.0