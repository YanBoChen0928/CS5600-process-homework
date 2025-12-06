#!/usr/bin/env python3
"""
medrag CLI - Unified command-line interface for Medical RAG Profiling
Supports: run, monitor, analyze, visualize, batch, compare, report, latex
Author: Yan-Bo Chen
"""

import argparse
import subprocess
import sys
from pathlib import Path
import platform
import psutil
import json
import glob
import statistics
import numpy as np

# ==== Helper: detect CPU architecture ======================================
def detect_arch():
    machine = platform.machine()
    if machine == "arm64":
        return "ARM"
    if machine in ["x86_64", "AMD64"]:
        return "x86"
    return "Unknown"

# ==== Helper: maps dataset names to files ==================================
QUERY_MAP = {
    "10": "queries/medical_queries_10.json",
    "25": "queries/medical_queries_25.json",
    "100": "queries/medical_queries_100.json",

    # category queries
    "cardio": "queries/cardio_queries.json",
    "infection": "queries/infection_queries.json",
    "trauma": "queries/trauma_queries.json",
}

# ==== Helper: dataset name to folder mapping ===============================
DATASET_FOLDERS = {
    "10": ("results/ARM_10", "results/x86_10"),
    "25": ("results/ARM_25", "results/x86_25"),
    "100": ("results/ARM_100", "results/x86_100"),
    "cardio": ("results/ARM_cardio", "results/x86_cardio"),
    "infection": ("results/ARM_infection", "results/x86_infection"),
    "trauma": ("results/ARM_trauma", "results/x86_trauma"),
}

# ============================================================================    
#                               COMMAND: RUN
# ============================================================================    
def cmd_run(args):
    dataset = args.dataset.lower()

    if dataset not in QUERY_MAP:
        print(f"❌ Unknown dataset '{dataset}'. Available: {list(QUERY_MAP.keys())}")
        sys.exit(1)

    query_file = QUERY_MAP[dataset]

    # Output folder name: smart naming based on dataset type
    if args.prefix:
        output_dir = args.prefix
    elif dataset in ["10", "25", "100"]:
        # Numeric sets: test_25x5, test_100x5
        output_dir = f"test_{dataset}x{args.runs}"
    else:
        # Category sets: profiling_cardio, profiling_infection
        output_dir = f"profiling_{dataset}"

    arch = detect_arch()
    
    cmd = [
        sys.executable,
        "run_experiment.py",
        "--queries", query_file,
        "--runs", str(args.runs),
        "--model", args.model,
        "--output", output_dir
    ]

    print("=" * 80)
    print(" MEDICAL RAG PROFILING - EXPERIMENT RUNNER".center(80))
    print("=" * 80)
    print(f" Dataset:      {dataset}")
    print(f" Query File:   {query_file}")
    print(f" Runs:         {args.runs}")
    print(f" Model:        {args.model}")
    print(f" Architecture: {arch}")
    print(f" Output Dir:   {output_dir}")
    print("=" * 80)
    print()

    subprocess.run(cmd)

# ============================================================================    
#                           COMMAND: MONITOR
# ============================================================================    
def cmd_monitor(args):
    cmd = [
        sys.executable,
        "monitor_experiment.py",
        args.output
    ]
    subprocess.run(cmd)

# ============================================================================    
#                           COMMAND: ANALYZE
# ============================================================================    
def cmd_analyze(args):
    cmd = [
        sys.executable,
        "analyze_results.py",
        args.output
    ]
    subprocess.run(cmd)

# ============================================================================    
#                         COMMAND: VISUALIZE
# ============================================================================    
def cmd_visualize(args):
    cmd = [
        sys.executable,
        "visualize_results.py",
        args.output
    ]
    subprocess.run(cmd)

# ============================================================================    
#                           COMMAND: BATCH
# ============================================================================    
def cmd_batch(args):
    """Run multiple experiments in sequence"""
    import time
    
    print()
    print("=" * 80)
    print("   BATCH EXPERIMENT MODE - ARM M2 Pro Data Collection".center(80))
    print("=" * 80)
    print()
    
    # Define experiment sets
    if args.all:
        experiments = [
            ('cardio', 5),
            ('infection', 5),
            ('trauma', 5),
            ('100', 5)
        ]
        print("Running ALL experiments:")
    elif args.categories:
        experiments = [
            ('cardio', 5),
            ('infection', 5),
            ('trauma', 5)
        ]
        print("Running CATEGORY experiments:")
    else:
        print("❌ Error: Specify --all or --categories")
        sys.exit(1)
    
    # Display plan
    for i, (dataset, runs) in enumerate(experiments, 1):
        query_file = QUERY_MAP[dataset]
        print(f"  {i}. {dataset:12s} ({runs} runs) → {query_file}")
    
    print()
    print("=" * 80)
    print()
    
    # Record start time
    batch_start = time.time()
    
    # Run each experiment
    for i, (dataset, runs) in enumerate(experiments, 1):
        exp_start = time.time()
        
        print()
        print("=" * 80)
        print(f"   [{i}/{len(experiments)}] Starting: {dataset.upper()} ({runs} runs)".center(80))
        print("=" * 80)
        print()
        
        # Prepare arguments for cmd_run
        class Args:
            pass
        
        run_args = Args()
        run_args.dataset = dataset
        run_args.runs = runs
        run_args.model = args.model
        run_args.prefix = None
        
        # Run experiment
        cmd_run(run_args)
        
        exp_duration = time.time() - exp_start
        exp_minutes = int(exp_duration / 60)
        exp_seconds = int(exp_duration % 60)
        
        print()
        print(f"✓ {dataset.upper()} completed in {exp_minutes}m {exp_seconds}s")
        print()
    
    # Summary
    batch_duration = time.time() - batch_start
    batch_hours = int(batch_duration / 3600)
    batch_minutes = int((batch_duration % 3600) / 60)
    
    print()
    print("=" * 80)
    print("   ALL BATCH EXPERIMENTS COMPLETE!".center(80))
    print("=" * 80)
    print()
    print(f"Total duration: {batch_hours}h {batch_minutes}m")
    print()
    print("Generated datasets:")
    for dataset, _ in experiments:
        if dataset in ['cardio', 'infection', 'trauma']:
            print(f"  ✓ profiling_{dataset}/")
        else:
            print(f"  ✓ profiling_data_{dataset}/")
    print()
    print("Next steps (tomorrow):")
    print("  ./medrag analyze --output profiling_cardio")
    print("  ./medrag visualize --output profiling_cardio")
    print("  (repeat for other datasets)")
    print()
    print("=" * 80)
    print()

# ============================================================================    
#                           COMMAND: COMPARE
# ============================================================================    
def cmd_compare(args):
    """Compare ARM vs x86 performance"""
    import matplotlib.pyplot as plt
    import numpy as np
    
    print()
    print("=" * 80)
    print("   ARM vs x86 PERFORMANCE COMPARISON".center(80))
    print("=" * 80)
    print()
    
    # Determine datasets to compare
    if args.all:
        datasets = ["25", "100", "cardio", "infection", "trauma"]
    elif args.dataset:
        datasets = [args.dataset]
    else:
        print("❌ Error: Specify --dataset <name> or --all")
        sys.exit(1)
    
    # Create output directory
    Path("final_report").mkdir(exist_ok=True)
    
    for dataset in datasets:
        if dataset not in DATASET_FOLDERS:
            print(f"⚠️  Warning: Unknown dataset '{dataset}', skipping...")
            continue
        
        arm_dir, x86_dir = DATASET_FOLDERS[dataset]
        
        # Check if both directories exist
        if not Path(arm_dir).exists():
            print(f"⚠️  Warning: ARM data not found: {arm_dir}")
            continue
        if not Path(x86_dir).exists():
            print(f"⚠️  Warning: x86 data not found: {x86_dir}")
            continue
        
        print(f"📊 Comparing: {dataset}")
        print(f"   ARM: {arm_dir}")
        print(f"   x86: {x86_dir}")
        
        # Load data from both platforms
        arm_data = load_experiment_data(arm_dir)
        x86_data = load_experiment_data(x86_dir)
        
        if not arm_data or not x86_data:
            print(f"   ⚠️  Insufficient data for comparison")
            continue
        
        # Extract metrics
        arm_latencies = [d['latency']['total_ms']/1000 for d in arm_data]
        x86_latencies = [d['latency']['total_ms']/1000 for d in x86_data]
        
        arm_cpu_peak = [d['timeline_summary']['cpu_peak_from_timeline'] for d in arm_data if 'timeline_summary' in d]
        x86_cpu_peak = [d['timeline_summary']['cpu_peak_from_timeline'] for d in x86_data if 'timeline_summary' in d]
        
        arm_cpu_avg = [d['timeline_summary']['cpu_avg_from_timeline'] for d in arm_data if 'timeline_summary' in d]
        x86_cpu_avg = [d['timeline_summary']['cpu_avg_from_timeline'] for d in x86_data if 'timeline_summary' in d]
        
        arm_memory = [d['timeline_summary']['memory_peak_from_timeline'] for d in arm_data if 'timeline_summary' in d]
        x86_memory = [d['timeline_summary']['memory_peak_from_timeline'] for d in x86_data if 'timeline_summary' in d]
        
        # Generate comparison plot (multi-panel)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Panel 1: Latency box plot
        ax1 = axes[0, 0]
        bp1 = ax1.boxplot([arm_latencies, x86_latencies], labels=['ARM M2 Pro', 'x86 + RTX 4090'],
                          patch_artist=True, showmeans=True)
        bp1['boxes'][0].set_facecolor('steelblue')
        bp1['boxes'][1].set_facecolor('coral')
        ax1.set_ylabel('Latency (seconds)', fontsize=11)
        ax1.set_title('Query Latency Distribution', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add speedup annotation
        speedup = statistics.median(arm_latencies) / statistics.median(x86_latencies)
        ax1.text(0.5, 0.95, f'Speedup: {speedup:.2f}×', transform=ax1.transAxes,
                fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        
        # Panel 2: CPU Peak comparison
        ax2 = axes[0, 1]
        cpu_means = [statistics.mean(arm_cpu_peak), statistics.mean(x86_cpu_peak)]
        cpu_stds = [statistics.stdev(arm_cpu_peak), statistics.stdev(x86_cpu_peak)]
        x_pos = [0, 1]
        bars2 = ax2.bar(x_pos, cpu_means, yerr=cpu_stds, capsize=5,
                       color=['steelblue', 'coral'], edgecolor='black', alpha=0.8)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(['ARM M2 Pro', 'x86 + RTX 4090'])
        ax2.set_ylabel('CPU Peak Usage (% total)', fontsize=11)
        ax2.set_title('CPU Peak Utilization', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Panel 3: CPU Average comparison
        ax3 = axes[1, 0]
        cpu_avg_means = [statistics.mean(arm_cpu_avg), statistics.mean(x86_cpu_avg)]
        cpu_avg_stds = [statistics.stdev(arm_cpu_avg), statistics.stdev(x86_cpu_avg)]
        bars3 = ax3.bar(x_pos, cpu_avg_means, yerr=cpu_avg_stds, capsize=5,
                       color=['steelblue', 'coral'], edgecolor='black', alpha=0.8)
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(['ARM M2 Pro', 'x86 + RTX 4090'])
        ax3.set_ylabel('CPU Average Usage (% total)', fontsize=11)
        ax3.set_title('CPU Average Utilization', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Panel 4: Memory comparison
        ax4 = axes[1, 1]
        mem_means = [statistics.mean(arm_memory), statistics.mean(x86_memory)]
        mem_stds = [statistics.stdev(arm_memory), statistics.stdev(x86_memory)]
        bars4 = ax4.bar(x_pos, mem_means, yerr=mem_stds, capsize=5,
                       color=['steelblue', 'coral'], edgecolor='black', alpha=0.8)
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(['ARM M2 Pro', 'x86 + RTX 4090'])
        ax4.set_ylabel('Memory Usage (GB)', fontsize=11)
        ax4.set_title('Memory Footprint', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # Save figure
        output_file = f'final_report/comparison_ARM_vs_x86_{dataset}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"   ✓ Saved: {output_file}")
        plt.close()
        
        print()
    
    print("=" * 80)
    print(f"✅ All comparison plots saved to: final_report/")
    print("=" * 80)
    print()

def load_experiment_data(output_dir):
    """Helper: Load all JSON data from experiment directory"""
    json_files = sorted(glob.glob(f'{output_dir}/query_*.json'))
    
    if not json_files:
        return None
    
    data = []
    for filepath in json_files:
        try:
            with open(filepath) as f:
                data.append(json.load(f))
        except Exception as e:
            print(f"   Warning: Error reading {filepath}: {e}")
    
    return data

# ============================================================================    
#                           COMMAND: REPORT
# ============================================================================    
def cmd_report(args):
    """Generate summary report (Markdown + CSV)"""
    print()
    print("=" * 80)
    print("   FINAL REPORT GENERATOR".center(80))
    print("=" * 80)
    print()
    
    # Determine datasets to report
    if args.all:
        datasets = ["25", "100", "cardio", "infection", "trauma"]
    elif args.dataset:
        datasets = [args.dataset]
    else:
        print("❌ Error: Specify --dataset <name> or --all")
        sys.exit(1)
    
    # Create output directory
    Path("final_report").mkdir(exist_ok=True)
    
    for dataset in datasets:
        if dataset not in DATASET_FOLDERS:
            print(f"⚠️  Warning: Unknown dataset '{dataset}', skipping...")
            continue
        
        arm_dir, x86_dir = DATASET_FOLDERS[dataset]
        
        # Check if both directories exist
        if not Path(arm_dir).exists() or not Path(x86_dir).exists():
            print(f"⚠️  Warning: Missing data for {dataset}")
            continue
        
        print(f"📝 Generating report: {dataset}")
        
        # Load data
        arm_data = load_experiment_data(arm_dir)
        x86_data = load_experiment_data(x86_dir)
        
        if not arm_data or not x86_data:
            print(f"   ⚠️  Insufficient data")
            continue
        
        # Calculate statistics
        arm_stats = calculate_statistics(arm_data)
        x86_stats = calculate_statistics(x86_data)
        
        # Generate Markdown report
        md_file = f'final_report/summary_ARM_vs_x86_{dataset}.md'
        generate_markdown_report(md_file, dataset, arm_stats, x86_stats)
        print(f"   ✓ Saved: {md_file}")
        
        # Generate CSV report
        csv_file = f'final_report/summary_ARM_vs_x86_{dataset}.csv'
        generate_csv_report(csv_file, arm_stats, x86_stats)
        print(f"   ✓ Saved: {csv_file}")
        
        print()
    
    print("=" * 80)
    print(f"✅ All reports saved to: final_report/")
    print("=" * 80)
    print()

def calculate_statistics(data):
    """Enhanced: Calculate comprehensive latency statistics including percentiles and P/E-cores"""
    latencies = [d['latency']['total_ms']/1000 for d in data]
    cpu_peaks = [d['timeline_summary']['cpu_peak_from_timeline'] for d in data if 'timeline_summary' in d]
    cpu_avgs = [d['timeline_summary']['cpu_avg_from_timeline'] for d in data if 'timeline_summary' in d]
    memory = [d['timeline_summary']['memory_peak_from_timeline'] for d in data if 'timeline_summary' in d]
    
    # NEW: P-cores and E-cores data (ARM-specific)
    p_cores_list = [d['cpu'].get('p_cores_average', 0) for d in data if 'cpu' in d and d['cpu'].get('p_cores_average') is not None]
    e_cores_list = [d['cpu'].get('e_cores_average', 0) for d in data if 'cpu' in d and d['cpu'].get('e_cores_average') is not None]
    
    # Calculate P/E-cores workload distribution
    p_cores_mean = statistics.mean(p_cores_list) if p_cores_list else 0
    e_cores_mean = statistics.mean(e_cores_list) if e_cores_list else 0
    total_core_work = p_cores_mean + e_cores_mean
    
    if total_core_work > 0:
        p_cores_workload_pct = (p_cores_mean / total_core_work) * 100
        e_cores_workload_pct = (e_cores_mean / total_core_work) * 100
    else:
        p_cores_workload_pct = 0
        e_cores_workload_pct = 0
    
    return {
        # === LATENCY METRICS ===
        'latency_median': statistics.median(latencies),  # p50
        'latency_mean': statistics.mean(latencies),
        'latency_stdev': statistics.stdev(latencies) if len(latencies) > 1 else 0,
        'latency_min': float(np.min(latencies)),
        'latency_p25': float(np.percentile(latencies, 25)),
        'latency_p75': float(np.percentile(latencies, 75)),
        'latency_p95': float(np.percentile(latencies, 95)),
        'latency_p99': float(np.percentile(latencies, 99)),
        'latency_max': float(np.max(latencies)),
        
        # === CPU METRICS ===
        'cpu_peak_mean': statistics.mean(cpu_peaks) if cpu_peaks else 0,
        'cpu_peak_stdev': statistics.stdev(cpu_peaks) if len(cpu_peaks) > 1 else 0,
        'cpu_avg_mean': statistics.mean(cpu_avgs) if cpu_avgs else 0,
        'cpu_avg_stdev': statistics.stdev(cpu_avgs) if len(cpu_avgs) > 1 else 0,
        
        # NEW: P-cores vs E-cores (ARM-specific)
        'p_cores_avg': p_cores_mean,
        'e_cores_avg': e_cores_mean,
        'p_cores_workload_pct': p_cores_workload_pct,
        'e_cores_workload_pct': e_cores_workload_pct,
        
        # === MEMORY METRICS ===
        'memory_mean': statistics.mean(memory) if memory else 0,
        'memory_stdev': statistics.stdev(memory) if len(memory) > 1 else 0,
        
        # === DERIVED METRICS ===
        'cores_used': statistics.mean(cpu_avgs) / 100.0 if cpu_avgs else 0,
        'num_queries': len(data)
    }

def generate_markdown_report(filename, dataset, arm_stats, x86_stats):
    """Enhanced: Include p95/p99 in markdown tables"""
    speedup = arm_stats['latency_median'] / x86_stats['latency_median']
    speedup_p95 = arm_stats['latency_p95'] / x86_stats['latency_p95']
    speedup_p99 = arm_stats['latency_p99'] / x86_stats['latency_p99']
    
    content = f"""# Performance Comparison: ARM vs x86 ({dataset})

**Date:** 2025-11-22  
**Dataset:** {dataset}  
**ARM Data Points:** {arm_stats['num_queries']}  
**x86 Data Points:** {x86_stats['num_queries']}

---

## Summary Statistics

| Metric                     | ARM M2 Pro | x86 + RTX 4090 | Speedup (x86/ARM) |
|---------------------------|------------|----------------|-------------------|
| **Latency (Min)**         | {arm_stats['latency_min']:.2f}s | {x86_stats['latency_min']:.2f}s | - |
| **Latency (p25)**         | {arm_stats['latency_p25']:.2f}s | {x86_stats['latency_p25']:.2f}s | - |
| **Latency (Median/p50)**  | {arm_stats['latency_median']:.2f}s | {x86_stats['latency_median']:.2f}s | {speedup:.2f}× |
| **Latency (p75)**         | {arm_stats['latency_p75']:.2f}s | {x86_stats['latency_p75']:.2f}s | - |
| **Latency (p95)** ⭐      | {arm_stats['latency_p95']:.2f}s | {x86_stats['latency_p95']:.2f}s | {speedup_p95:.2f}× |
| **Latency (p99)** ⭐      | {arm_stats['latency_p99']:.2f}s | {x86_stats['latency_p99']:.2f}s | {speedup_p99:.2f}× |
| **Latency (Max)**         | {arm_stats['latency_max']:.2f}s | {x86_stats['latency_max']:.2f}s | - |
| **Latency (Mean)**        | {arm_stats['latency_mean']:.2f}s | {x86_stats['latency_mean']:.2f}s | {arm_stats['latency_mean']/x86_stats['latency_mean']:.2f}× |
| **Latency (Std Dev)**     | {arm_stats['latency_stdev']:.2f}s | {x86_stats['latency_stdev']:.2f}s | - |
| **CPU Peak (Total %)**    | {arm_stats['cpu_peak_mean']:.1f}% | {x86_stats['cpu_peak_mean']:.1f}% | - |
| **CPU Average (Total %)** | {arm_stats['cpu_avg_mean']:.1f}% | {x86_stats['cpu_avg_mean']:.1f}% | - |
| **Memory Peak (GB)**      | {arm_stats['memory_mean']:.2f} | {x86_stats['memory_mean']:.2f} | - |
| **Cores Used (Avg)**      | {arm_stats['cores_used']:.1f} | {x86_stats['cores_used']:.1f} | - |

---

## Key Findings

### Performance
- **x86 + RTX 4090 is {speedup:.2f}× faster** than ARM M2 Pro (median latency)
- **Tail latency (p95):** ARM {arm_stats['latency_p95']:.2f}s vs x86 {x86_stats['latency_p95']:.2f}s ({speedup_p95:.2f}× difference)
- **Worst-case (p99):** ARM {arm_stats['latency_p99']:.2f}s vs x86 {x86_stats['latency_p99']:.2f}s ({speedup_p99:.2f}× difference)
- x86 shows {'lower' if x86_stats['latency_stdev'] < arm_stats['latency_stdev'] else 'higher'} latency variance ({x86_stats['latency_stdev']:.2f}s vs {arm_stats['latency_stdev']:.2f}s std dev)

### CPU Utilization
- ARM: ~{arm_stats['cores_used']:.1f} cores actively used on average
  - **P-cores (Performance)**: {arm_stats['p_cores_avg']:.2f}% avg utilization, {arm_stats['p_cores_workload_pct']:.1f}% of workload
  - **E-cores (Efficiency)**: {arm_stats['e_cores_avg']:.2f}% avg utilization, {arm_stats['e_cores_workload_pct']:.1f}% of workload
- x86: ~{x86_stats['cores_used']:.1f} cores actively used on average
- x86 exhibits {'higher' if x86_stats['cores_used'] > arm_stats['cores_used'] else 'lower'} parallelization efficiency

### Memory Footprint
- ARM: {arm_stats['memory_mean']:.2f} GB average (unified memory)
- x86: {x86_stats['memory_mean']:.2f} GB average (discrete memory)
- ARM shows {((arm_stats['memory_mean'] - x86_stats['memory_mean'])/x86_stats['memory_mean']*100):.0f}% {'lower' if arm_stats['memory_mean'] < x86_stats['memory_mean'] else 'higher'} memory usage

---

## Deployment Recommendations

### Use ARM M2 Pro when:
- Budget-constrained environments
- Edge deployment scenarios
- Power efficiency is critical
- Moderate latency requirements (p95 < {arm_stats['latency_p95']:.1f}s acceptable)

### Use x86 + RTX 4090 when:
- Low latency is critical (p95 < {x86_stats['latency_p95']:.1f}s required)
- Strict tail latency requirements (p99 < {x86_stats['latency_p99']:.1f}s)
- High throughput requirements
- GPU resources are available
- Budget allows for higher-end hardware
"""
    
    with open(filename, 'w') as f:
        f.write(content)

def generate_csv_report(filename, arm_stats, x86_stats):
    """Enhanced: Include all percentiles in CSV output"""
    speedup_median = arm_stats['latency_median'] / x86_stats['latency_median']
    speedup_mean = arm_stats['latency_mean'] / x86_stats['latency_mean']
    speedup_p95 = arm_stats['latency_p95'] / x86_stats['latency_p95']
    speedup_p99 = arm_stats['latency_p99'] / x86_stats['latency_p99']
    
    lines = [
        "Metric,ARM_M2_Pro,x86_RTX4090,Speedup",
        f"Latency_Min_s,{arm_stats['latency_min']:.2f},{x86_stats['latency_min']:.2f},",
        f"Latency_p25_s,{arm_stats['latency_p25']:.2f},{x86_stats['latency_p25']:.2f},",
        f"Latency_Median_s,{arm_stats['latency_median']:.2f},{x86_stats['latency_median']:.2f},{speedup_median:.2f}",
        f"Latency_p75_s,{arm_stats['latency_p75']:.2f},{x86_stats['latency_p75']:.2f},",
        f"Latency_p95_s,{arm_stats['latency_p95']:.2f},{x86_stats['latency_p95']:.2f},{speedup_p95:.2f}",
        f"Latency_p99_s,{arm_stats['latency_p99']:.2f},{x86_stats['latency_p99']:.2f},{speedup_p99:.2f}",
        f"Latency_Max_s,{arm_stats['latency_max']:.2f},{x86_stats['latency_max']:.2f},",
        f"Latency_Mean_s,{arm_stats['latency_mean']:.2f},{x86_stats['latency_mean']:.2f},{speedup_mean:.2f}",
        f"Latency_StdDev_s,{arm_stats['latency_stdev']:.2f},{x86_stats['latency_stdev']:.2f},",
        f"CPU_Peak_Percent,{arm_stats['cpu_peak_mean']:.1f},{x86_stats['cpu_peak_mean']:.1f},",
        f"CPU_Average_Percent,{arm_stats['cpu_avg_mean']:.1f},{x86_stats['cpu_avg_mean']:.1f},",
        f"CPU_P_Cores_Avg_Percent,{arm_stats['p_cores_avg']:.2f},{x86_stats.get('p_cores_avg', 0):.2f},",
        f"CPU_E_Cores_Avg_Percent,{arm_stats['e_cores_avg']:.2f},{x86_stats.get('e_cores_avg', 0):.2f},",
        f"CPU_P_Cores_Workload_Pct,{arm_stats['p_cores_workload_pct']:.1f},{x86_stats.get('p_cores_workload_pct', 0):.1f},",
        f"CPU_E_Cores_Workload_Pct,{arm_stats['e_cores_workload_pct']:.1f},{x86_stats.get('e_cores_workload_pct', 0):.1f},",
        f"Memory_Peak_GB,{arm_stats['memory_mean']:.2f},{x86_stats['memory_mean']:.2f},",
        f"Cores_Used_Avg,{arm_stats['cores_used']:.1f},{x86_stats['cores_used']:.1f},",
    ]
    
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

# ============================================================================    
#                           COMMAND: LATEX
# ============================================================================    
def cmd_latex(args):
    """Generate LaTeX tables"""
    print()
    print("=" * 80)
    print("   LATEX TABLE GENERATOR".center(80))
    print("=" * 80)
    print()
    
    # Determine datasets
    if args.all:
        datasets = ["25", "100", "cardio", "infection", "trauma"]
    elif args.dataset:
        datasets = [args.dataset]
    else:
        print("❌ Error: Specify --dataset <name> or --all")
        sys.exit(1)
    
    # Create output directory
    Path("final_report").mkdir(exist_ok=True)
    
    for dataset in datasets:
        if dataset not in DATASET_FOLDERS:
            print(f"⚠️  Warning: Unknown dataset '{dataset}', skipping...")
            continue
        
        arm_dir, x86_dir = DATASET_FOLDERS[dataset]
        
        # Check if both directories exist
        if not Path(arm_dir).exists() or not Path(x86_dir).exists():
            print(f"⚠️  Warning: Missing data for {dataset}")
            continue
        
        print(f"📄 Generating LaTeX table: {dataset}")
        
        # Load data
        arm_data = load_experiment_data(arm_dir)
        x86_data = load_experiment_data(x86_dir)
        
        if not arm_data or not x86_data:
            print(f"   ⚠️  Insufficient data")
            continue
        
        # Calculate statistics
        arm_stats = calculate_statistics(arm_data)
        x86_stats = calculate_statistics(x86_data)
        
        # Generate LaTeX table
        tex_file = f'final_report/table_{dataset}.tex'
        generate_latex_table(tex_file, dataset, arm_stats, x86_stats)
        print(f"   ✓ Saved: {tex_file}")
        
        print()
    
    print("=" * 80)
    print(f"✅ All LaTeX tables saved to: final_report/")
    print("=" * 80)
    print()
    print("Usage in LaTeX:")
    print("  \\usepackage{booktabs}")
    print("  \\input{final_report/table_100.tex}")
    print()

def generate_latex_table(filename, dataset, arm_stats, x86_stats):
    """Enhanced: LaTeX table with p95/p99"""
    speedup_median = arm_stats['latency_median'] / x86_stats['latency_median']
    speedup_mean = arm_stats['latency_mean'] / x86_stats['latency_mean']
    speedup_p95 = arm_stats['latency_p95'] / x86_stats['latency_p95']
    speedup_p99 = arm_stats['latency_p99'] / x86_stats['latency_p99']
    
    content = f"""\\begin{{table}}[htbp]
\\centering
\\caption{{Performance Comparison: ARM M2 Pro vs x86 + RTX 4090 ({dataset})}}
\\label{{tab:perf_comparison_{dataset}}}
\\begin{{tabular}}{{lrrr}}
\\toprule
\\textbf{{Metric}} & \\textbf{{ARM M2 Pro}} & \\textbf{{x86 + RTX 4090}} & \\textbf{{Speedup}} \\\\
\\midrule
\\multicolumn{{4}}{{l}}{{\\textit{{Latency (seconds)}}}} \\\\
\\quad Min         & {arm_stats['latency_min']:.2f} & {x86_stats['latency_min']:.2f}  & -- \\\\
\\quad p25         & {arm_stats['latency_p25']:.2f} & {x86_stats['latency_p25']:.2f}  & -- \\\\
\\quad Median (p50)& {arm_stats['latency_median']:.2f} & {x86_stats['latency_median']:.2f}  & {speedup_median:.2f}$\\times$ \\\\
\\quad p75         & {arm_stats['latency_p75']:.2f} & {x86_stats['latency_p75']:.2f}  & -- \\\\
\\quad p95         & {arm_stats['latency_p95']:.2f} & {x86_stats['latency_p95']:.2f}  & {speedup_p95:.2f}$\\times$ \\\\
\\quad p99         & {arm_stats['latency_p99']:.2f} & {x86_stats['latency_p99']:.2f}  & {speedup_p99:.2f}$\\times$ \\\\
\\quad Max         & {arm_stats['latency_max']:.2f} & {x86_stats['latency_max']:.2f}  & -- \\\\
\\quad Mean        & {arm_stats['latency_mean']:.2f} & {x86_stats['latency_mean']:.2f}  & {speedup_mean:.2f}$\\times$ \\\\
\\quad Std Dev     & {arm_stats['latency_stdev']:.2f}  & {x86_stats['latency_stdev']:.2f}  & -- \\\\
\\midrule
\\multicolumn{{4}}{{l}}{{\\textit{{CPU Utilization (\\%)}}}} \\\\
\\quad Peak        & {arm_stats['cpu_peak_mean']:.1f} & {x86_stats['cpu_peak_mean']:.1f} & -- \\\\
\\quad Average     & {arm_stats['cpu_avg_mean']:.1f} & {x86_stats['cpu_avg_mean']:.1f}  & -- \\\\
\\quad Cores Used  & {arm_stats['cores_used']:.1f}   & {x86_stats['cores_used']:.1f}    & -- \\\\
\\midrule
\\multicolumn{{4}}{{l}}{{\\textit{{Memory (GB)}}}} \\\\
\\quad Peak        & {arm_stats['memory_mean']:.2f}  & {x86_stats['memory_mean']:.2f}   & -- \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    
    with open(filename, 'w') as f:
        f.write(content)

# ============================================================================    
#                              MAIN CLI
# ============================================================================    
def main():
    parser = argparse.ArgumentParser(
        prog="medrag",
        description="Unified CLI for Medical RAG Profiling"
    )

    subparsers = parser.add_subparsers(dest="command")

    # ----- run --------------------------------------------------------------
    p_run = subparsers.add_parser("run", help="Run RAG profiling experiment")
    p_run.add_argument("--dataset",
                       required=True,
                       help="10 / 25 / 100 / cardio / infection / trauma")
    p_run.add_argument("--runs",
                       type=int,
                       default=1,
                       help="How many runs per query")
    p_run.add_argument("--model",
                       default="llama3.2-cpu",
                       help="Model name used by RAG wrapper")
    p_run.add_argument("--prefix",
                       default=None,
                       help="Optional output prefix")
    p_run.set_defaults(func=cmd_run)

    # ----- monitor ----------------------------------------------------------
    p_monitor = subparsers.add_parser("monitor", help="Monitor experiment (real-time)")
    p_monitor.add_argument("--output",
                           required=True,
                           help="Output directory to monitor")
    p_monitor.set_defaults(func=cmd_monitor)

    # ----- analyze ----------------------------------------------------------
    p_analyze = subparsers.add_parser("analyze", help="Analyze finished experiment")
    p_analyze.add_argument("--output",
                           required=True,
                           help="Output directory")
    p_analyze.set_defaults(func=cmd_analyze)

    # ----- visualize --------------------------------------------------------
    p_visual = subparsers.add_parser("visualize", help="Generate plots & heatmaps")
    p_visual.add_argument("--output",
                          required=True,
                          help="Output directory")
    p_visual.set_defaults(func=cmd_visualize)

    # ----- batch ------------------------------------------------------------
    p_batch = subparsers.add_parser("batch", help="Run multiple experiments in sequence")
    batch_group = p_batch.add_mutually_exclusive_group(required=True)
    batch_group.add_argument("--all",
                            action="store_true",
                            help="Run all experiments (categories + 100×5)")
    batch_group.add_argument("--categories",
                            action="store_true",
                            help="Run only category experiments (cardio/infection/trauma)")
    p_batch.add_argument("--model",
                        default="llama3.2-cpu",
                        help="Model name")
    p_batch.set_defaults(func=cmd_batch)

    # ----- compare ----------------------------------------------------------
    p_compare = subparsers.add_parser("compare", help="Compare ARM vs x86 performance")
    compare_group = p_compare.add_mutually_exclusive_group(required=True)
    compare_group.add_argument("--dataset",
                              help="Dataset to compare: 25 / 100 / cardio / infection / trauma")
    compare_group.add_argument("--all",
                              action="store_true",
                              help="Compare all datasets")
    p_compare.set_defaults(func=cmd_compare)

    # ----- report -----------------------------------------------------------
    p_report = subparsers.add_parser("report", help="Generate summary report (Markdown + CSV)")
    report_group = p_report.add_mutually_exclusive_group(required=True)
    report_group.add_argument("--dataset",
                             help="Dataset to report: 25 / 100 / cardio / infection / trauma")
    report_group.add_argument("--all",
                             action="store_true",
                             help="Generate reports for all datasets")
    p_report.set_defaults(func=cmd_report)

    # ----- latex ------------------------------------------------------------
    p_latex = subparsers.add_parser("latex", help="Generate LaTeX tables for paper")
    latex_group = p_latex.add_mutually_exclusive_group(required=True)
    latex_group.add_argument("--dataset",
                            help="Dataset to generate table: 25 / 100 / cardio / infection / trauma")
    latex_group.add_argument("--all",
                            action="store_true",
                            help="Generate LaTeX tables for all datasets")
    p_latex.set_defaults(func=cmd_latex)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
