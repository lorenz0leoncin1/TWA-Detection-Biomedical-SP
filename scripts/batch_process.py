"""
Batch processing script for multiple ECG records
Usage: python scripts/batch_process.py --input-dir data/raw/ --output-dir results/
"""

import argparse
import sys
from pathlib import Path
import json
import time

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from twa_detection import ECGPreprocessor, CorrelationMethod
from twa_detection.utils import load_ecg_data, save_results


def process_record(record_path, output_dir, channel=0, n_beats=128, min_alternating=7):
    """Process a single ECG record"""
    record_name = record_path.stem
    
    try:
        # Load data
        ecg, fs, _ = load_ecg_data(str(record_path), channel=channel)
        
        # Preprocess
        preprocessor = ECGPreprocessor(fs=fs)
        prep_results = preprocessor.preprocess(ecg, n_beats=n_beats)
        
        # Detect TWA
        cm = CorrelationMethod(min_alternating_beats=min_alternating)
        twa_results = cm.analyze(prep_results['t_waves'])
        
        # Save results
        output_file = output_dir / f"{record_name}_twa_results.json"
        save_results(twa_results, prep_results, str(output_file))
        
        return {
            'record': record_name,
            'status': 'success',
            'twa_detected': twa_results['twa_detected'],
            'magnitude': twa_results['magnitude']
        }
        
    except Exception as e:
        return {
            'record': record_name,
            'status': 'error',
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(
        description='Batch process multiple ECG records for TWA detection'
    )
    parser.add_argument(
        '--input-dir', '-i',
        type=str,
        required=True,
        help='Input directory containing ECG records'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='results/batch/',
        help='Output directory for results (default: results/batch/)'
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
        '--pattern',
        type=str,
        default='*.hea',
        help='File pattern to match (default: *.hea)'
    )
    
    args = parser.parse_args()
    
    # Setup directories
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return 1
    
    # Find all records
    records = list(input_dir.glob(args.pattern))
    
    if not records:
        print(f"Error: No records found matching pattern '{args.pattern}' in {input_dir}")
        return 1
    
    print(f"\n{'='*70}")
    print(f"BATCH T-WAVE ALTERNANS ANALYSIS")
    print(f"{'='*70}")
    print(f"Input directory:  {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Records found:    {len(records)}")
    print(f"{'='*70}\n")
    
    # Process records
    results = []
    start_time = time.time()
    
    for i, record_path in enumerate(records, 1):
        record_name = record_path.stem
        print(f"[{i}/{len(records)}] Processing {record_name}...", end=' ')
        
        result = process_record(
            record_path,
            output_dir,
            channel=args.channel,
            n_beats=args.n_beats
        )
        
        results.append(result)
        
        if result['status'] == 'success':
            twa_status = 'TWA+' if result['twa_detected'] else 'TWA-'
            mag = result.get('magnitude', 0)
            print(f"✓ {twa_status} (mag: {mag:.1f} µV)")
        else:
            print(f"✗ Error: {result['error']}")
    
    # Summary
    elapsed_time = time.time() - start_time
    successful = sum(1 for r in results if r['status'] == 'success')
    twa_positive = sum(1 for r in results if r.get('twa_detected', False))
    
    print(f"\n{'='*70}")
    print(f"BATCH PROCESSING SUMMARY")
    print(f"{'='*70}")
    print(f"Total records:     {len(records)}")
    print(f"Successful:        {successful} ({successful/len(records)*100:.1f}%)")
    print(f"Failed:            {len(records) - successful}")
    print(f"TWA detected:      {twa_positive} ({twa_positive/successful*100:.1f}% of successful)")
    print(f"Processing time:   {elapsed_time:.1f} seconds")
    print(f"Average time:      {elapsed_time/len(records):.2f} sec/record")
    print(f"{'='*70}\n")
    
    # Save summary
    summary_file = output_dir / 'batch_summary.json'
    with open(summary_file, 'w') as f:
        json.dump({
            'total_records': len(records),
            'successful': successful,
            'twa_positive': twa_positive,
            'processing_time_seconds': elapsed_time,
            'results': results
        }, f, indent=2)
    
    print(f"Summary saved to: {summary_file}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())