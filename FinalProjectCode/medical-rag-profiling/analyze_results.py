#!/usr/bin/env python3
"""
Experiment Results Analysis
Generates statistical reports from profiling data
"""

import json
import glob
import sys
from pathlib import Path
import statistics

def analyze_experiment(output_dir):
    """Analyze all profiling results and generate report"""
    
    print()
    print("=" * 80)
    print("MEDICAL RAG PROFILING - ANALYSIS REPORT".center(80))
    print("=" * 80)
    print()
    
    # Find all query JSON files
    json_files = sorted(glob.glob(f'{output_dir}/query_*.json'))
    
    if not json_files:
        print(f"❌ Error: No data files found in '{output_dir}'")
        print(f"   Make sure the experiment has completed.")
        return
    
    # Collect data
    latencies = []
    cpu_peaks = []
    cpu_avgs = []
    memory_used = []
    timeline_samples = []
    response_lengths = []
    
    for filepath in json_files:
        try:
            with open(filepath) as f:
                data = json.load(f)
                
                # Latency
                latencies.append(data['latency']['total_ms'])
                
                # Timeline CPU data (most accurate)
                if 'timeline_summary' in data:
                    cpu_peaks.append(data['timeline_summary']['cpu_peak_from_timeline'])
                    cpu_avgs.append(data['timeline_summary']['cpu_avg_from_timeline'])
                    memory_used.append(data['timeline_summary']['memory_peak_from_timeline'])
                    timeline_samples.append(data['timeline_summary']['num_samples'])
                
                # Response length
                if 'response' in data:
                    response_lengths.append(data['response']['length_chars'])
        
        except Exception as e:
            print(f"Warning: Error reading {filepath}: {e}")
    
    # Generate report
    print(f"📁 Dataset: {output_dir}")
    print(f"📊 Total Queries Analyzed: {len(json_files)}")
    print()
    
    # Latency Analysis
    print("⏱️  LATENCY ANALYSIS (seconds)")
    print("-" * 80)
    print(f"   Minimum:       {min(latencies)/1000:7.2f}s")
    print(f"   Maximum:       {max(latencies)/1000:7.2f}s")
    print(f"   Median:        {statistics.median(latencies)/1000:7.2f}s")
    print(f"   Mean:          {statistics.mean(latencies)/1000:7.2f}s")
    print(f"   Std Deviation: {statistics.stdev(latencies)/1000:7.2f}s")
    print()
    
    # CPU Analysis (Timeline Data - Most Accurate)
    print("⚡ CPU USAGE ANALYSIS (Timeline - All Cores Total %)")
    print("-" * 80)
    print("   Peak Load:")
    print(f"      Minimum:  {min(cpu_peaks):7.1f}%")
    print(f"      Maximum:  {max(cpu_peaks):7.1f}%")
    print(f"      Mean:     {statistics.mean(cpu_peaks):7.1f}%")
    print()
    print("   Average Load:")
    print(f"      Minimum:  {min(cpu_avgs):7.1f}%")
    print(f"      Maximum:  {max(cpu_avgs):7.1f}%")
    print(f"      Mean:     {statistics.mean(cpu_avgs):7.1f}%")
    print()
    
    # Per-core interpretation
    mean_cpu_avg = statistics.mean(cpu_avgs)
    per_core_avg = mean_cpu_avg / 12
    print(f"   Per-Core Average: {per_core_avg:.1f}% (= {mean_cpu_avg:.1f}% ÷ 12 cores)")
    print(f"   Interpretation: ~{mean_cpu_avg/100:.1f} cores actively running on average")
    print()
    
    # Memory Analysis
    print("💾 MEMORY USAGE ANALYSIS (GB)")
    print("-" * 80)
    print(f"   Minimum:  {min(memory_used):6.2f} GB")
    print(f"   Maximum:  {max(memory_used):6.2f} GB")
    print(f"   Mean:     {statistics.mean(memory_used):6.2f} GB")
    print(f"   Range:    {max(memory_used) - min(memory_used):6.2f} GB")
    
    if max(memory_used) - min(memory_used) < 0.5:
        print(f"   ✓ Memory stable (range < 0.5 GB) - No memory leaks detected")
    else:
        print(f"   ⚠ Memory range > 0.5 GB - Check for potential memory growth")
    print()
    
    # Response Quality
    print("📝 RESPONSE QUALITY")
    print("-" * 80)
    print(f"   Average Length: {statistics.mean(response_lengths):.0f} characters")
    print(f"   Min Length:     {min(response_lengths)} characters")
    print(f"   Max Length:     {max(response_lengths)} characters")
    print()
    
    # Timeline Sampling
    print("📈 TIMELINE SAMPLING")
    print("-" * 80)
    print(f"   Samples per Query (avg): {statistics.mean(timeline_samples):.1f}")
    print(f"   Min Samples: {min(timeline_samples)}")
    print(f"   Max Samples: {max(timeline_samples)}")
    print()
    
    # System characterization
    print("🎯 SYSTEM CHARACTERIZATION SUMMARY")
    print("-" * 80)
    print(f"   Workload Type:     CPU-Intensive (avg {mean_cpu_avg:.0f}% total CPU usage)")
    print(f"   Core Utilization:  ~{mean_cpu_avg/100:.1f} out of 12 cores actively used")
    print(f"   Memory Footprint:  ~{statistics.mean(memory_used):.1f} GB")
    print(f"   Response Time:     {statistics.mean(latencies)/1000:.1f}s ± {statistics.stdev(latencies)/1000:.1f}s")
    print()
    
    print("=" * 80)
    print()

if __name__ == '__main__':
    output_dir = sys.argv[1] if len(sys.argv) > 1 else 'phase3_stress'
    analyze_experiment(output_dir)
