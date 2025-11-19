"""
Single ECG record analysis script
Usage: python scripts/run_analysis.py --input data/raw/record_001 --output results/
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from twa_detection import ECGPreprocessor, CorrelationMethod
from twa_detection.utils import load_ecg_data, plot_results, save_results, print_summary


def main():
    parser = argparse.ArgumentParser(
        description='Analyze ECG record for T-Wave Alternans'
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Path to input ECG record (without extension)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='results/',
        help='Output directory for results (default: results/)'
    )
    parser.add_argument(
        '--channel',
        type=int,
        default=0,
        help='ECG channel to analyze (default: 0)'
    )
    parser.add_argument(
        '--n-beats',
        type=int,
        default=128,
        help='Number of beats to analyze (default: 128)'
    )
    parser.add_argument(
        '--min-alternating',
        type=int,
        default=7,
        help='Minimum alternating beats for TWA detection (default: 7)'
    )
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Generate and save plots'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get record name
    record_path = Path(args.input)
    record_name = record_path.stem
    
    if args.verbose:
        print(f"\n{'='*60}")
        print(f"T-WAVE ALTERNANS ANALYSIS")
        print(f"{'='*60}")
        print(f"Record: {record_name}")
        print(f"Channel: {args.channel}")
        print(f"Output: {output_dir}")
        print(f"{'='*60}\n")
    
    try:
        # Load ECG data
        if args.verbose:
            print("Loading ECG data...")
        
        ecg, fs, metadata = load_ecg_data(str(record_path), channel=args.channel)
        
        if args.verbose:
            print(f"  ✓ Loaded {len(ecg)} samples at {fs} Hz")
            print(f"  ✓ Duration: {len(ecg)/fs:.1f} seconds")
            print(f"  ✓ Signal: {metadata['sig_name']}")
        
        # Preprocessing
        if args.verbose:
            print("\nPreprocessing ECG...")
        
        preprocessor = ECGPreprocessor(fs=fs)
        prep_results = preprocessor.preprocess(ecg, n_beats=args.n_beats)
        
        if args.verbose:
            print(f"  ✓ Detected {len(prep_results['r_peaks'])} R peaks")
            print(f"  ✓ RR stability: {'Stable' if prep_results['is_stable'] else 'Unstable'}")
            print(f"  ✓ Extracted {len(prep_results['t_waves'])} T waves")
        
        # TWA Detection
        if args.verbose:
            print("\nDetecting T-Wave Alternans...")
        
        cm = CorrelationMethod(min_alternating_beats=args.min_alternating)
        twa_results = cm.analyze(prep_results['t_waves'])
        
        # Print results
        print_summary(twa_results)
        
        # Save results
        json_path = output_dir / f"{record_name}_twa_results.json"
        save_results(twa_results, prep_results, str(json_path))
        
        if args.verbose:
            print(f"Results saved to: {json_path}")
        
        # Generate plots
        if args.plot:
            if args.verbose:
                print("\nGenerating plots...")
            
            fig_path = output_dir / f"{record_name}_twa_analysis.png"
            plot_results(ecg, twa_results, prep_results, save_path=str(fig_path))
            
            if args.verbose:
                print(f"Figure saved to: {fig_path}")
        
        if args.verbose:
            print(f"\n{'='*60}")
            print("Analysis completed successfully!")
            print(f"{'='*60}\n")
        
        return 0
        
    except FileNotFoundError:
        print(f"Error: ECG record not found: {args.input}")
        print("Make sure the file exists and the path is correct.")
        return 1
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())