#!/usr/bin/env python3
"""
Real-time Experiment Monitor
Displays Timeline-style CPU data during experiment execution
"""

import json
import time
import os
import sys
from pathlib import Path
from datetime import datetime

def monitor_experiment(output_dir='phase3_stress'):
    """Monitor experiment progress with Timeline CPU data"""
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print(f"Warning: Directory '{output_dir}' does not exist yet.")
        print("Waiting for experiment to start...")
        print()
    
    try:
        while True:
            os.system('clear')
            
            # Header
            print("=" * 80)
            print("MEDICAL RAG PROFILING - REAL-TIME MONITOR".center(80))
            print("=" * 80)
            print(f"Monitoring: {output_dir}")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
            print()
            
            # Find all JSON files
            json_files = sorted(output_path.glob('query_*.json')) if output_path.exists() else []
            
            if json_files:
                latest = json_files[-1]
                
                try:
                    with open(latest) as f:
                        data = json.load(f)
                    
                    # Current query info
                    query_id = data['metadata']['query_id']
                    run_id = data['metadata']['run_id']
                    query_text = data['metadata']['query_text'][:70]
                    
                    print(f"📊 LATEST COMPLETED QUERY")
                    print(f"   Query ID: {query_id}, Run: {run_id}")
                    print(f"   Text: {query_text}...")
                    print()
                    
                    # Timeline CPU data (most accurate)
                    if 'timeline_summary' in data:
                        summary = data['timeline_summary']
                        
                        print(f"⚡ CPU USAGE (Timeline - All Cores Total)")
                        print(f"   Peak:    {summary['cpu_peak_from_timeline']:7.1f}%  (Max load across all cores)")
                        print(f"   Average: {summary['cpu_avg_from_timeline']:7.1f}%  (Sustained load)")
                        print()
                        
                        # Convert to per-core average for context
                        avg_per_core = summary['cpu_avg_from_timeline'] / 12
                        print(f"   Per-Core Average: {avg_per_core:.1f}% (= {summary['cpu_avg_from_timeline']:.1f}% ÷ 12 cores)")
                        print()
                        
                        print(f"💾 MEMORY")
                        print(f"   Peak: {summary['memory_peak_from_timeline']:.2f} GB")
                        print()
                        
                        print(f"⏱️  LATENCY")
                        print(f"   Total: {data['latency']['total_ms']/1000:.2f} seconds")
                        print()
                        
                        print(f"📈 TIMELINE SAMPLING")
                        print(f"   Samples Collected: {summary['num_samples']}")
                    
                    print()
                    print("-" * 80)
                    print(f"📁 PROGRESS")
                    print(f"   Completed Queries: {len(json_files)}")
                    
                    # Try to estimate progress if config exists
                    config_file = output_path / 'experiment_config.json'
                    if config_file.exists():
                        with open(config_file) as f:
                            config = json.load(f)
                            total = config['experiment_metadata']['total_profiles']
                            progress = (len(json_files) / total) * 100
                            print(f"   Total Expected: {total}")
                            print(f"   Progress: {progress:.1f}%")
                    
                except Exception as e:
                    print(f"Error reading latest file: {e}")
            
            else:
                print("⏳ Waiting for experiment to start...")
                print(f"   Looking for files in: {output_dir}")
            
            print()
            print("=" * 80)
            print("Press Ctrl+C to stop monitoring".center(80))
            print("=" * 80)
            
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n\n✓ Monitoring stopped.\n")
        sys.exit(0)

if __name__ == '__main__':
    output_dir = sys.argv[1] if len(sys.argv) > 1 else 'phase3_stress'
    monitor_experiment(output_dir)
