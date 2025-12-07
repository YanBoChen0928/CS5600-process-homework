#!/usr/bin/env python3
"""
Experiment Results Visualization
Generates publication-ready plots and heatmaps
"""

import json
import glob
import sys
import platform
import psutil
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style for publication-quality plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def detect_cpu_architecture():
    """Detect CPU type and core layout (ARM vs x86)"""
    machine = platform.machine()
    
    if machine == 'arm64':
        # ARM (M1/M2/M3) with heterogeneous cores
        # M2 Pro 12-core: 8 P-cores (0-7) + 4 E-cores (8-11)
        return {
            'type': 'ARM',
            'total_cores': 12,
            'p_cores': 8,
            'e_cores': 4,
            'has_heterogeneous': True
        }
    elif machine in ['x86_64', 'AMD64']:
        # x86 - assume homogeneous cores
        cores = psutil.cpu_count(logical=False)  # Physical cores only
        return {
            'type': 'x86',
            'total_cores': cores,
            'p_cores': cores,
            'e_cores': 0,
            'has_heterogeneous': False
        }
    else:
        # Fallback for unknown architectures
        cores = psutil.cpu_count(logical=False)
        return {
            'type': 'Unknown',
            'total_cores': cores,
            'p_cores': cores,
            'e_cores': 0,
            'has_heterogeneous': False
        }

def load_experiment_data(output_dir):
    """Load all experiment data from JSON files"""
    json_files = sorted(glob.glob(f'{output_dir}/query_*.json'))
    
    if not json_files:
        print(f"❌ Error: No data files found in '{output_dir}'")
        return None
    
    data = []
    for filepath in json_files:
        try:
            with open(filepath) as f:
                data.append(json.load(f))
        except Exception as e:
            print(f"Warning: Error reading {filepath}: {e}")
    
    return data

def create_cpu_heatmap(data, output_dir, arch):
    """Create CPU utilization heatmap (12 cores × timeline) - Hardware Adaptive"""
    print("📊 Generating CPU Heatmap...")
    
    # Select a representative query with good timeline data
    # Find query with median CPU usage
    cpu_avgs = [d['timeline_summary']['cpu_avg_from_timeline'] for d in data if 'timeline_summary' in d]
    median_cpu = np.median(cpu_avgs)
    
    # Find query closest to median
    best_query = None
    min_diff = float('inf')
    for d in data:
        if 'timeline_summary' in d and 'timeline' in d:
            diff = abs(d['timeline_summary']['cpu_avg_from_timeline'] - median_cpu)
            if diff < min_diff:
                min_diff = diff
                best_query = d
    
    if not best_query:
        print("   ⚠️  No suitable query found for heatmap")
        return
    
    # Extract timeline data
    timeline = best_query['timeline']
    num_samples = len(timeline)
    num_cores = len(timeline[0]['cpu_cores'])  # Auto-detect from data
    
    # Build matrix: rows = cores, columns = time samples
    cpu_matrix = np.zeros((num_cores, num_samples))
    time_points = []
    
    for i, sample in enumerate(timeline):
        time_points.append(sample['t'])
        for core_idx, core_usage in enumerate(sample['cpu_cores']):
            cpu_matrix[core_idx, i] = core_usage
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot heatmap
    im = ax.imshow(cpu_matrix, aspect='auto', cmap='YlOrRd', 
                   interpolation='nearest', vmin=0, vmax=100)
    
    # Set labels
    ax.set_xlabel('Time (seconds)', fontsize=12)
    ax.set_ylabel('CPU Core', fontsize=12)
    ax.set_title(f'CPU Core Utilization Over Time\n'
                 f'Query {best_query["metadata"]["query_id"]}: {best_query["metadata"]["query_text"][:60]}...',
                 fontsize=14, fontweight='bold')
    
    # Set y-axis (cores) - ADAPTIVE LABELS
    if arch['has_heterogeneous']:
        # ARM: P-cores and E-cores
        y_labels = [f'Core {i}' + (' (P)' if i < arch['p_cores'] else ' (E)') 
                    for i in range(num_cores)]
    else:
        # x86: All cores equal
        y_labels = [f'Core {i}' for i in range(num_cores)]
    
    ax.set_yticks(range(num_cores))
    ax.set_yticklabels(y_labels)
    
    # Set x-axis (time)
    # Show time labels at regular intervals
    num_ticks = min(10, num_samples)
    tick_indices = np.linspace(0, num_samples-1, num_ticks, dtype=int)
    ax.set_xticks(tick_indices)
    ax.set_xticklabels([f'{time_points[i]:.1f}' for i in tick_indices])
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('CPU Usage (%)', rotation=270, labelpad=20, fontsize=11)
    
    # Add horizontal line to separate P-cores and E-cores (ARM only)
    if arch['has_heterogeneous']:
        ax.axhline(y=arch['p_cores']-0.5, color='blue', linestyle='--', linewidth=2, alpha=0.5)
        ax.text(num_samples * 0.02, arch['p_cores']/2 - 0.5, 'P-cores', fontsize=10, color='blue', 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        ax.text(num_samples * 0.02, arch['p_cores'] + (num_cores - arch['p_cores'])/2, 'E-cores', 
                fontsize=10, color='blue', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    plt.tight_layout()
    
    # Save figure
    output_file = f'{output_dir}/cpu_heatmap.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: {output_file}")
    
    plt.close()

def create_latency_distribution(data, output_dir):
    """Create latency distribution histogram"""
    print("📊 Generating Latency Distribution...")
    
    latencies = [d['latency']['total_ms'] / 1000 for d in data]  # Convert to seconds
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create histogram
    n, bins, patches = ax.hist(latencies, bins=15, edgecolor='black', alpha=0.7, color='steelblue')
    
    # Add mean and median lines
    mean_lat = np.mean(latencies)
    median_lat = np.median(latencies)
    
    ax.axvline(mean_lat, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_lat:.2f}s')
    ax.axvline(median_lat, color='green', linestyle='--', linewidth=2, label=f'Median: {median_lat:.2f}s')
    
    # Labels
    ax.set_xlabel('Latency (seconds)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Query Latency Distribution', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_file = f'{output_dir}/latency_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: {output_file}")
    
    plt.close()

def create_memory_timeline(data, output_dir):
    """Create memory usage timeline"""
    print("📊 Generating Memory Timeline...")
    
    query_ids = [d['metadata']['query_id'] for d in data]
    memory_peaks = [d['timeline_summary']['memory_peak_from_timeline'] for d in data if 'timeline_summary' in d]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot memory usage
    ax.plot(query_ids, memory_peaks, marker='o', linewidth=2, markersize=6, color='purple')
    ax.fill_between(query_ids, memory_peaks, alpha=0.3, color='purple')
    
    # Add mean line
    mean_memory = np.mean(memory_peaks)
    ax.axhline(mean_memory, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_memory:.2f} GB')
    
    # Labels
    ax.set_xlabel('Query ID', fontsize=12)
    ax.set_ylabel('Memory Usage (GB)', fontsize=12)
    ax.set_title('Memory Usage Across Queries', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Set y-axis to start from a reasonable minimum
    ax.set_ylim([min(memory_peaks) - 0.2, max(memory_peaks) + 0.2])
    
    plt.tight_layout()
    
    # Save figure
    output_file = f'{output_dir}/memory_timeline.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: {output_file}")
    
    plt.close()

def create_core_utilization_comparison(data, output_dir, arch):
    """Compare P-cores vs E-cores utilization - Hardware Adaptive"""
    print("📊 Generating Core Utilization Comparison...")
    
    num_cores = arch['total_cores']
    
    # Collect per-core averages across all queries
    core_usage = [[] for _ in range(num_cores)]
    
    for d in data:
        if 'timeline' not in d:
            continue
        
        # Average each core across the timeline
        for sample in d['timeline']:
            cores = sample['cpu_cores']
            for i in range(min(num_cores, len(cores))):
                core_usage[i].append(cores[i])
    
    # Calculate averages
    core_avgs = [np.mean(core) if core else 0 for core in core_usage]
    
    # Create comparison plot
    if arch['has_heterogeneous']:
        # ARM: Split into P-cores and E-cores
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        p_core_avgs = core_avgs[:arch['p_cores']]
        e_core_avgs = core_avgs[arch['p_cores']:]
        
        # P-cores
        cores_p = list(range(arch['p_cores']))
        ax1.bar(cores_p, p_core_avgs, color='steelblue', edgecolor='black', alpha=0.8)
        ax1.set_xlabel('P-Core ID', fontsize=12)
        ax1.set_ylabel('Average CPU Usage (%)', fontsize=12)
        ax1.set_title('Performance Cores (P-cores)', fontsize=13, fontweight='bold')
        ax1.set_xticks(cores_p)
        ax1.set_xticklabels([f'Core {i}' for i in cores_p])
        ax1.set_ylim([0, 100])
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.axhline(np.mean(p_core_avgs), color='red', linestyle='--', linewidth=2, 
                    label=f'Mean: {np.mean(p_core_avgs):.1f}%')
        ax1.legend()
        
        # E-cores
        cores_e = list(range(len(e_core_avgs)))
        ax2.bar(cores_e, e_core_avgs, color='coral', edgecolor='black', alpha=0.8)
        ax2.set_xlabel('E-Core ID', fontsize=12)
        ax2.set_ylabel('Average CPU Usage (%)', fontsize=12)
        ax2.set_title('Efficiency Cores (E-cores)', fontsize=13, fontweight='bold')
        ax2.set_xticks(cores_e)
        ax2.set_xticklabels([f'Core {i+arch["p_cores"]}' for i in cores_e])
        ax2.set_ylim([0, 100])
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.axhline(np.mean(e_core_avgs), color='red', linestyle='--', linewidth=2,
                    label=f'Mean: {np.mean(e_core_avgs):.1f}%')
        ax2.legend()
    
    else:
        # x86: Single plot for all cores
        fig, ax = plt.subplots(figsize=(14, 6))
        
        cores_all = list(range(num_cores))
        ax.bar(cores_all, core_avgs, color='steelblue', edgecolor='black', alpha=0.8)
        ax.set_xlabel('Core ID', fontsize=12)
        ax.set_ylabel('Average CPU Usage (%)', fontsize=12)
        ax.set_title('CPU Core Utilization', fontsize=13, fontweight='bold')
        ax.set_xticks(cores_all)
        ax.set_xticklabels([f'Core {i}' for i in cores_all])
        ax.set_ylim([0, 100])
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(np.mean(core_avgs), color='red', linestyle='--', linewidth=2,
                   label=f'Mean: {np.mean(core_avgs):.1f}%')
        ax.legend()
    
    plt.tight_layout()
    
    # Save figure
    output_file = f'{output_dir}/core_utilization_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: {output_file}")
    
    plt.close()

def create_cpu_timeline_aggregate(data, output_dir):
    """Create aggregate CPU timeline (all queries)"""
    print("📊 Generating Aggregate CPU Timeline...")
    
    # Collect CPU total across all queries
    all_timelines = []
    
    for d in data:
        if 'timeline' not in d:
            continue
        
        timeline = d['timeline']
        cpu_totals = [sample['cpu_total'] for sample in timeline]
        time_points = [sample['t'] for sample in timeline]
        
        all_timelines.append((time_points, cpu_totals))
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot each query with transparency
    for i, (times, cpus) in enumerate(all_timelines):
        ax.plot(times, cpus, alpha=0.3, linewidth=1, color='steelblue')
    
    # Calculate and plot average
    # Normalize time to percentage of completion
    max_samples = max(len(t[0]) for t in all_timelines)
    avg_cpu = []
    
    for sample_idx in range(max_samples):
        sample_cpus = []
        for times, cpus in all_timelines:
            # Map to normalized position
            if sample_idx < len(cpus):
                sample_cpus.append(cpus[sample_idx])
        if sample_cpus:
            avg_cpu.append(np.mean(sample_cpus))
    
    norm_time = np.linspace(0, 100, len(avg_cpu))
    ax.plot(norm_time, avg_cpu, color='red', linewidth=3, label='Average', zorder=10)
    
    # Labels
    ax.set_xlabel('Query Progress (%)', fontsize=12)
    ax.set_ylabel('Total CPU Usage (% across all cores)', fontsize=12)
    ax.set_title('CPU Usage Timeline - All Queries', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1300])
    
    # Add reference lines
    ax.axhline(1200, color='orange', linestyle='--', alpha=0.5, label='Peak (1200%)')
    ax.axhline(800, color='green', linestyle='--', alpha=0.5, label='Target (800%)')
    
    plt.tight_layout()
    
    # Save figure
    output_file = f'{output_dir}/cpu_timeline_aggregate.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: {output_file}")
    
    plt.close()

def main():
    """Main visualization function"""
    output_dir = sys.argv[1] if len(sys.argv) > 1 else 'phase3_stress'
    
    # Detect CPU architecture
    arch = detect_cpu_architecture()
    
    print()
    print("=" * 80)
    print("MEDICAL RAG PROFILING - VISUALIZATION GENERATOR".center(80))
    print("=" * 80)
    print()
    print(f"📁 Dataset: {output_dir}")
    print(f"🖥️  CPU Architecture: {arch['type']}")
    print(f"💻 Total Cores: {arch['total_cores']}")
    if arch['has_heterogeneous']:
        print(f"   P-cores: {arch['p_cores']}, E-cores: {arch['e_cores']}")
    print()
    
    # Load data
    data = load_experiment_data(output_dir)
    if not data:
        return
    
    print(f"✓ Loaded {len(data)} queries")
    print()
    
    # Generate visualizations
    create_cpu_heatmap(data, output_dir, arch)
    create_latency_distribution(data, output_dir)
    create_memory_timeline(data, output_dir)
    create_core_utilization_comparison(data, output_dir, arch)
    create_cpu_timeline_aggregate(data, output_dir)
    
    print()
    print("=" * 80)
    print(f"✅ All visualizations saved to: {output_dir}/")
    print("=" * 80)
    print()
    print("Generated files:")
    print("  • cpu_heatmap.png                  - Core-by-core CPU utilization heatmap")
    print("  • latency_distribution.png         - Response time distribution")
    print("  • memory_timeline.png              - Memory usage across queries")
    print("  • core_utilization_comparison.png  - P-cores vs E-cores comparison")
    print("  • cpu_timeline_aggregate.png       - Aggregate CPU timeline")
    print()

if __name__ == '__main__':
    main()
