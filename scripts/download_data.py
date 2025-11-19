"""
Download MUSIC database from PhysioNet
Usage: python scripts/download_data.py --output data/raw/ --n-records 10
"""

import argparse
import sys
from pathlib import Path
import subprocess


def download_physionet_record(database, record, output_dir):
    """Download a single record from PhysioNet using wget"""
    base_url = f"https://physionet.org/files/{database}/1.0.1/"
    
    files = [f"{record}.hea", f"{record}.dat"]
    
    for file in files:
        url = base_url + file
        output_path = output_dir / file
        
        try:
            subprocess.run(
                ["wget", "-q", "-O", str(output_path), url],
                check=True
            )
        except subprocess.CalledProcessError:
            # Try with curl if wget fails
            try:
                subprocess.run(
                    ["curl", "-s", "-o", str(output_path), url],
                    check=True
                )
            except subprocess.CalledProcessError:
                return False
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Download ECG records from PhysioNet MUSIC database'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='data/raw/',
        help='Output directory (default: data/raw/)'
    )
    parser.add_argument(
        '--n-records',
        type=int,
        default=10,
        help='Number of records to download (default: 10)'
    )
    parser.add_argument(
        '--database',
        type=str,
        default='music-sudden-cardiac-death',
        help='PhysioNet database name'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"DOWNLOADING PHYSIONET DATA")
    print(f"{'='*60}")
    print(f"Database: {args.database}")
    print(f"Output:   {output_dir}")
    print(f"Records:  {args.n_records}")
    print(f"{'='*60}\n")
    
    # MUSIC database has records named music_001 to music_139
    # Download first n_records
    
    successful = 0
    failed = 0
    
    for i in range(1, args.n_records + 1):
        record = f"music_{i:03d}"
        print(f"[{i}/{args.n_records}] Downloading {record}...", end=' ')
        
        if download_physionet_record(args.database, record, output_dir):
            print("✓")
            successful += 1
        else:
            print("✗ Failed")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Download complete!")
    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")
    print(f"{'='*60}\n")
    
    if successful == 0:
        print("ERROR: No records downloaded successfully.")
        print("Please check your internet connection and try again.")
        print("Alternatively, download manually from:")
        print(f"https://physionet.org/content/{args.database}/1.0.1/")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())