#!/usr/bin/env python3
"""
Advanced Visualization Script for Medical RAG Profiling
Generates publication-ready plots including:
- Box plots with p95/p99 markers
- Violin plots by dataset
- CDF (Cumulative Distribution Function) plots
- Dataset comparison matrices

Author: Yan-Bo Chen
Date: December 2025
Project: CS5600 Medical RAG Workload Characterization
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for publication-quality plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Default paths
RESULTS_DIR = Path("results")
OUTPUT_DIR = Path("final_report")


# =============================================================================
# Task 1: Core Data Functions
# =============================================================================

def collect_latencies(result_dir: str) -> List[float]:
    """
    Collect all latency values from a directory of profiling results.
    
    Args:
        result_dir: Path to results directory (e.g., "results/ARM_100")
    
    Returns:
        List of latency values in seconds
    """
    latencies = []
    result_path = Path(result_dir)
    
    if not result_path.exists():
        print(f"   Warning: Directory not found: {result_dir}")
        return latencies
    
    # Iterate through all JSON files matching query pattern
    for json_file in sorted(result_path.glob("query_*_run_*.json")):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                if data.get("success", False):
                    # Convert from milliseconds to seconds
                    latency_s = data["latency"]["total_ms"] / 1000.0
                    latencies.append(latency_s)
        except Exception as e:
            print(f"   Warning: Failed to read {json_file}: {e}")
    
    return latencies


def calculate_percentiles(latencies: List[float]) -> Dict[str, float]:
    """
    Calculate comprehensive latency percentiles.
    
    Args:
        latencies: List of latency values in seconds
    
    Returns:
        Dictionary with percentile values (min, p25, p50, p75, p95, p99, max, mean, std)
    """
    if not latencies:
        return {
            "min": 0, "p25": 0, "p50": 0, "p75": 0,
            "p95": 0, "p99": 0, "max": 0, "mean": 0, "std": 0, "count": 0
        }
    
    arr = np.array(latencies)
    return {
        "min": float(np.min(arr)),
        "p25": float(np.percentile(arr, 25)),
        "p50": float(np.percentile(arr, 50)),  # median
        "p75": float(np.percentile(arr, 75)),
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
        "max": float(np.max(arr)),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "count": len(latencies)
    }


def print_percentiles_report(name: str, percentiles: Dict[str, float]) -> None:
    """Print formatted percentiles report to console."""
    print(f"\n{'='*60}")
    print(f"Latency Percentiles: {name}")
    print(f"{'='*60}")
    print(f"Count:  {percentiles['count']:8d} queries")
    print(f"Min:    {percentiles['min']:8.2f} s")
    print(f"P25:    {percentiles['p25']:8.2f} s")
    print(f"P50:    {percentiles['p50']:8.2f} s (median)")
    print(f"P75:    {percentiles['p75']:8.2f} s")
    print(f"P95:    {percentiles['p95']:8.2f} s")
    print(f"P99:    {percentiles['p99']:8.2f} s")
    print(f"Max:    {percentiles['max']:8.2f} s")
    print(f"Mean:   {percentiles['mean']:8.2f} s ± {percentiles['std']:.2f}")
    print(f"{'='*60}\n")


# =============================================================================
# Task 2: Box Plot with p95/p99 Markers
# =============================================================================

def plot_latency_boxplot(arm_dir: str, x86_dir: str, output_file: str, 
                         dataset_name: str = "100") -> None:
    """
    Create box plot comparing ARM vs x86 latency distribution with p95/p99 markers.
    
    Args:
        arm_dir: Path to ARM results directory
        x86_dir: Path to x86 results directory
        output_file: Output PNG file path
        dataset_name: Name of the dataset for title
    """
    print(f"📊 Generating Box Plot: {dataset_name}...")
    
    # Collect data
    arm_latencies = collect_latencies(arm_dir)
    x86_latencies = collect_latencies(x86_dir)
    
    if not arm_latencies or not x86_latencies:
        print(f"   ⚠️ Insufficient data for {dataset_name}")
        return
    
    # Calculate percentiles
    arm_pct = calculate_percentiles(arm_latencies)
    x86_pct = calculate_percentiles(x86_latencies)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Prepare data for box plot
    data = [arm_latencies, x86_latencies]
    labels = ['ARM M2 Pro\n(CPU-only)', 'x86 + RTX 4090\n(GPU)']
    positions = [1, 2]
    
    # Create box plot with custom styling
    bp = ax.boxplot(data, positions=positions, widths=0.5,
                    patch_artist=True,
                    showfliers=True,
                    flierprops=dict(marker='o', markerfacecolor='gray', 
                                   markersize=4, alpha=0.5))
    
    # Color the boxes
    colors = ['#3498db', '#e74c3c']  # Blue for ARM, Red for x86
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    # Set median line color
    for median in bp['medians']:
        median.set_color('black')
        median.set_linewidth(2)
    
    # Add p95 markers with horizontal lines and annotations
    # ARM p95
    ax.hlines(arm_pct['p95'], 0.65, 1.35, colors='orange', linestyles='--', 
              linewidth=2, label='p95')
    ax.annotate(f"p95: {arm_pct['p95']:.1f}s", 
                xy=(1.4, arm_pct['p95']), fontsize=9, color='orange',
                verticalalignment='center')
    
    # ARM p99
    ax.hlines(arm_pct['p99'], 0.65, 1.35, colors='red', linestyles='--', 
              linewidth=2, label='p99')
    ax.annotate(f"p99: {arm_pct['p99']:.1f}s", 
                xy=(1.4, arm_pct['p99']), fontsize=9, color='red',
                verticalalignment='center')
    
    # x86 p95
    ax.hlines(x86_pct['p95'], 1.65, 2.35, colors='orange', linestyles='--', 
              linewidth=2)
    ax.annotate(f"p95: {x86_pct['p95']:.1f}s", 
                xy=(2.4, x86_pct['p95']), fontsize=9, color='orange',
                verticalalignment='center')
    
    # x86 p99
    ax.hlines(x86_pct['p99'], 1.65, 2.35, colors='red', linestyles='--', 
              linewidth=2)
    ax.annotate(f"p99: {x86_pct['p99']:.1f}s", 
                xy=(2.4, x86_pct['p99']), fontsize=9, color='red',
                verticalalignment='center')
    
    # Add mean markers
    ax.scatter([1], [arm_pct['mean']], marker='D', color='green', s=80, 
               zorder=3, label=f"Mean")
    ax.scatter([2], [x86_pct['mean']], marker='D', color='green', s=80, zorder=3)
    
    # Labels and title
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel('Latency (seconds)', fontsize=12)
    ax.set_title(f'Query Latency Distribution: ARM vs x86\n'
                 f'Dataset: {dataset_name} (n={arm_pct["count"]}/{x86_pct["count"]})',
                 fontsize=14, fontweight='bold')
    
    # Add grid
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_axisbelow(True)
    
    # Create custom legend
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor='#3498db', alpha=0.6, label='ARM M2 Pro'),
        Patch(facecolor='#e74c3c', alpha=0.6, label='x86 + RTX 4090'),
        Line2D([0], [0], color='orange', linestyle='--', linewidth=2, label='p95'),
        Line2D([0], [0], color='red', linestyle='--', linewidth=2, label='p99'),
        Line2D([0], [0], marker='D', color='w', markerfacecolor='green', 
               markersize=8, label='Mean')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    # Adjust layout and save
    plt.tight_layout()
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: {output_file}")
    plt.close()


# =============================================================================
# Task 3: Violin Plot by Dataset
# =============================================================================

def plot_latency_violin_by_dataset(datasets: List[str], platform: str, 
                                    output_file: str) -> None:
    """
    Create violin plot comparing latency across different datasets for one platform.
    
    Args:
        datasets: List of dataset names (e.g., ["cardio", "infection", "trauma"])
        platform: "ARM" or "x86"
        output_file: Output PNG file path
    """
    print(f"📊 Generating Violin Plot: {platform} across datasets...")
    
    # Collect data for all datasets
    all_data = []
    all_labels = []
    
    for dataset in datasets:
        result_dir = RESULTS_DIR / f"{platform}_{dataset}"
        latencies = collect_latencies(str(result_dir))
        
        if latencies:
            for lat in latencies:
                all_data.append({"Dataset": dataset.capitalize(), "Latency (s)": lat})
            all_labels.append(dataset.capitalize())
    
    if not all_data:
        print(f"   ⚠️ No data found for {platform}")
        return
    
    # Convert to numpy arrays for violin plot
    import pandas as pd
    df = pd.DataFrame(all_data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Create violin plot (assign hue to avoid FutureWarning)
    palette = sns.color_palette("Set2", len(datasets))
    parts = sns.violinplot(data=df, x="Dataset", y="Latency (s)", 
                           hue="Dataset", palette=palette, inner="quartile", 
                           ax=ax, legend=False)
    
    # Calculate and add mean markers
    dataset_means = df.groupby("Dataset")["Latency (s)"].mean()
    dataset_p95 = df.groupby("Dataset")["Latency (s)"].quantile(0.95)
    dataset_p99 = df.groupby("Dataset")["Latency (s)"].quantile(0.99)
    
    for i, dataset in enumerate([d.capitalize() for d in datasets]):
        if dataset in dataset_means.index:
            ax.scatter([i], [dataset_means[dataset]], color='red', s=100, 
                      zorder=3, marker='D', edgecolor='black', linewidth=1)
            
            # Add p95/p99 text annotations
            ax.annotate(f"p95: {dataset_p95[dataset]:.1f}s\np99: {dataset_p99[dataset]:.1f}s",
                       xy=(i + 0.35, dataset_p95[dataset]), fontsize=8,
                       verticalalignment='center')
    
    # Labels and title
    ax.set_xlabel('Medical Domain', fontsize=12)
    ax.set_ylabel('Latency (seconds)', fontsize=12)
    
    platform_name = "ARM M2 Pro (CPU-only)" if platform == "ARM" else "x86 + RTX 4090 (GPU)"
    ax.set_title(f'Query Latency Distribution by Medical Domain\n'
                 f'Platform: {platform_name}',
                 fontsize=14, fontweight='bold')
    
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_axisbelow(True)
    
    # Add legend for mean marker
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='D', color='w', markerfacecolor='red',
               markeredgecolor='black', markersize=10, label='Mean')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    # Adjust layout and save
    plt.tight_layout()
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: {output_file}")
    plt.close()


# =============================================================================
# Task 4: CDF Plot
# =============================================================================

def plot_latency_cdf(arm_dir: str, x86_dir: str, output_file: str,
                     dataset_name: str = "100") -> None:
    """
    Create CDF (Cumulative Distribution Function) plot comparing ARM vs x86.
    
    Args:
        arm_dir: Path to ARM results directory
        x86_dir: Path to x86 results directory
        output_file: Output PNG file path
        dataset_name: Name of the dataset for title
    """
    print(f"📊 Generating CDF Plot: {dataset_name}...")
    
    # Collect and sort data
    arm_latencies = np.sort(collect_latencies(arm_dir))
    x86_latencies = np.sort(collect_latencies(x86_dir))
    
    if len(arm_latencies) == 0 or len(x86_latencies) == 0:
        print(f"   ⚠️ Insufficient data for {dataset_name}")
        return
    
    # Calculate CDF values
    arm_cdf = np.arange(1, len(arm_latencies) + 1) / len(arm_latencies)
    x86_cdf = np.arange(1, len(x86_latencies) + 1) / len(x86_latencies)
    
    # Calculate percentiles
    arm_p95 = np.percentile(arm_latencies, 95)
    arm_p99 = np.percentile(arm_latencies, 99)
    x86_p95 = np.percentile(x86_latencies, 95)
    x86_p99 = np.percentile(x86_latencies, 99)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(11, 7))
    
    # Plot CDF curves
    ax.plot(arm_latencies, arm_cdf, label='ARM M2 Pro (CPU-only)', 
            linewidth=2.5, color='#3498db')
    ax.plot(x86_latencies, x86_cdf, label='x86 + RTX 4090 (GPU)', 
            linewidth=2.5, color='#e74c3c')
    
    # Add horizontal reference lines at p95 and p99
    ax.axhline(0.95, color='gray', linestyle=':', linewidth=1.5, alpha=0.7)
    ax.axhline(0.99, color='gray', linestyle=':', linewidth=1.5, alpha=0.7)
    
    # Add vertical lines at percentile values
    ax.axvline(arm_p95, color='#3498db', linestyle='--', linewidth=1.5, alpha=0.6)
    ax.axvline(arm_p99, color='#3498db', linestyle='-.', linewidth=1.5, alpha=0.6)
    ax.axvline(x86_p95, color='#e74c3c', linestyle='--', linewidth=1.5, alpha=0.6)
    ax.axvline(x86_p99, color='#e74c3c', linestyle='-.', linewidth=1.5, alpha=0.6)
    
    # Add annotations for percentile values
    y_offset = 0.02
    ax.annotate(f'ARM p95: {arm_p95:.1f}s', xy=(arm_p95, 0.95 + y_offset),
                fontsize=9, color='#3498db', ha='center')
    ax.annotate(f'ARM p99: {arm_p99:.1f}s', xy=(arm_p99, 0.99 + y_offset),
                fontsize=9, color='#3498db', ha='center')
    ax.annotate(f'x86 p95: {x86_p95:.1f}s', xy=(x86_p95, 0.95 - y_offset - 0.03),
                fontsize=9, color='#e74c3c', ha='center')
    ax.annotate(f'x86 p99: {x86_p99:.1f}s', xy=(x86_p99, 0.99 - y_offset - 0.03),
                fontsize=9, color='#e74c3c', ha='center')
    
    # Add text labels for reference lines
    ax.text(ax.get_xlim()[1] * 0.98, 0.95, '95%', fontsize=9, 
            va='center', ha='right', color='gray')
    ax.text(ax.get_xlim()[1] * 0.98, 0.99, '99%', fontsize=9, 
            va='center', ha='right', color='gray')
    
    # Labels and title
    ax.set_xlabel('Latency (seconds)', fontsize=12)
    ax.set_ylabel('Cumulative Probability', fontsize=12)
    ax.set_title(f'Latency Cumulative Distribution Function (CDF)\n'
                 f'Dataset: {dataset_name}',
                 fontsize=14, fontweight='bold')
    
    ax.set_ylim([0, 1.02])
    ax.set_xlim([0, None])
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, loc='lower right')
    
    # Adjust layout and save
    plt.tight_layout()
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: {output_file}")
    plt.close()


# =============================================================================
# Task 5: Dataset Comparison Matrix
# =============================================================================

def plot_dataset_comparison_matrix(platform: str, datasets: List[str],
                                    output_file: str) -> None:
    """
    Create 2x2 comparison matrix for multiple datasets.
    
    Args:
        platform: "ARM" or "x86"
        datasets: List of dataset names (e.g., ["cardio", "infection", "trauma"])
        output_file: Output PNG file path
    """
    print(f"📊 Generating Comparison Matrix: {platform}...")
    
    # Collect data for all datasets
    data_dict = {}
    for dataset in datasets:
        result_dir = RESULTS_DIR / f"{platform}_{dataset}"
        latencies = collect_latencies(str(result_dir))
        
        if latencies:
            pct = calculate_percentiles(latencies)
            data_dict[dataset] = {
                'latencies': latencies,
                **pct
            }
    
    if not data_dict:
        print(f"   ⚠️ No data found for {platform}")
        return
    
    available_datasets = list(data_dict.keys())
    
    # Create 2x2 subplot figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    platform_name = "ARM M2 Pro (CPU-only)" if platform == "ARM" else "x86 + RTX 4090 (GPU)"
    fig.suptitle(f'Dataset Comparison Matrix: {platform_name}', 
                 fontsize=16, fontweight='bold', y=1.02)
    
    # Color palette
    colors = sns.color_palette("Set2", len(available_datasets))
    
    # -------------------------------------------------------------------------
    # Plot 1: Mean Latency with Error Bars (Top-Left)
    # -------------------------------------------------------------------------
    ax1 = axes[0, 0]
    means = [data_dict[d]['mean'] for d in available_datasets]
    stds = [data_dict[d]['std'] for d in available_datasets]
    x_pos = np.arange(len(available_datasets))
    
    bars1 = ax1.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, 
                    color=colors, edgecolor='black', linewidth=1)
    
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([d.capitalize() for d in available_datasets])
    ax1.set_ylabel('Mean Latency (seconds)')
    ax1.set_title('Mean Latency by Dataset\n(with std dev error bars)', fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_axisbelow(True)
    
    # Add value labels on bars
    for i, (bar, mean, std) in enumerate(zip(bars1, means, stds)):
        ax1.annotate(f'{mean:.1f}s', xy=(bar.get_x() + bar.get_width()/2, mean + std + 0.5),
                    ha='center', va='bottom', fontsize=9)
    
    # -------------------------------------------------------------------------
    # Plot 2: p95 vs p99 Comparison (Top-Right)
    # -------------------------------------------------------------------------
    ax2 = axes[0, 1]
    width = 0.35
    p95_values = [data_dict[d]['p95'] for d in available_datasets]
    p99_values = [data_dict[d]['p99'] for d in available_datasets]
    
    bars_p95 = ax2.bar(x_pos - width/2, p95_values, width, label='p95', 
                       alpha=0.7, color='orange', edgecolor='black')
    bars_p99 = ax2.bar(x_pos + width/2, p99_values, width, label='p99', 
                       alpha=0.7, color='red', edgecolor='black')
    
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([d.capitalize() for d in available_datasets])
    ax2.set_ylabel('Latency (seconds)')
    ax2.set_title('Tail Latency Comparison\n(p95 vs p99)', fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_axisbelow(True)
    
    # Add value labels
    for bar in bars_p95:
        height = bar.get_height()
        ax2.annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    ha='center', va='bottom', fontsize=8)
    for bar in bars_p99:
        height = bar.get_height()
        ax2.annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    ha='center', va='bottom', fontsize=8)
    
    # -------------------------------------------------------------------------
    # Plot 3: Violin Distribution Comparison (Bottom-Left)
    # -------------------------------------------------------------------------
    ax3 = axes[1, 0]
    violin_data = [data_dict[d]['latencies'] for d in available_datasets]
    
    parts = ax3.violinplot(violin_data, positions=x_pos, showmeans=True, 
                           showmedians=True, widths=0.7)
    
    # Color the violins
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.6)
    
    # Style the mean and median lines
    parts['cmeans'].set_color('red')
    parts['cmeans'].set_linewidth(2)
    parts['cmedians'].set_color('black')
    parts['cmedians'].set_linewidth(2)
    
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels([d.capitalize() for d in available_datasets])
    ax3.set_ylabel('Latency (seconds)')
    ax3.set_title('Latency Distribution Comparison\n(Violin Plot)', fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_axisbelow(True)
    
    # Add legend for violin
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='red', linewidth=2, label='Mean'),
        Line2D([0], [0], color='black', linewidth=2, label='Median')
    ]
    ax3.legend(handles=legend_elements, loc='upper right', fontsize=9)
    
    # -------------------------------------------------------------------------
    # Plot 4: Statistics Table (Bottom-Right)
    # -------------------------------------------------------------------------
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # Build statistics text
    stats_text = "Dataset Statistics Summary\n" + "=" * 45 + "\n"
    
    for dataset in available_datasets:
        d = data_dict[dataset]
        stats_text += f"\n{dataset.upper()}:\n"
        stats_text += f"  Samples:  {d['count']:>6d}\n"
        stats_text += f"  Min:      {d['min']:>6.2f} s\n"
        stats_text += f"  Mean:     {d['mean']:>6.2f} s ± {d['std']:.2f}\n"
        stats_text += f"  Median:   {d['p50']:>6.2f} s\n"
        stats_text += f"  p95:      {d['p95']:>6.2f} s\n"
        stats_text += f"  p99:      {d['p99']:>6.2f} s\n"
        stats_text += f"  Max:      {d['max']:>6.2f} s\n"
    
    ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes,
             fontsize=10, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Adjust layout and save
    plt.tight_layout()
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: {output_file}")
    plt.close()


# =============================================================================
# Task 6: Main CLI Interface
# =============================================================================

def generate_all_visualizations() -> None:
    """Generate all visualization types for all datasets."""
    print("\n" + "=" * 70)
    print("GENERATING ALL ADVANCED VISUALIZATIONS")
    print("=" * 70 + "\n")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Define datasets
    datasets_100 = "100"
    specialized_datasets = ["cardio", "infection", "trauma"]
    
    # 1. Box Plots for each dataset
    print("\n[1/4] Box Plots with p95/p99 markers...")
    for dataset in [datasets_100] + specialized_datasets:
        arm_dir = str(RESULTS_DIR / f"ARM_{dataset}")
        x86_dir = str(RESULTS_DIR / f"x86_{dataset}")
        output_file = str(OUTPUT_DIR / f"boxplot_{dataset}.png")
        plot_latency_boxplot(arm_dir, x86_dir, output_file, dataset)
    
    # 2. Violin Plots for each platform
    print("\n[2/4] Violin Plots by dataset...")
    for platform in ["ARM", "x86"]:
        output_file = str(OUTPUT_DIR / f"violin_{platform}.png")
        plot_latency_violin_by_dataset(specialized_datasets, platform, output_file)
    
    # 3. CDF Plots for each dataset
    print("\n[3/4] CDF Plots...")
    for dataset in [datasets_100] + specialized_datasets:
        arm_dir = str(RESULTS_DIR / f"ARM_{dataset}")
        x86_dir = str(RESULTS_DIR / f"x86_{dataset}")
        output_file = str(OUTPUT_DIR / f"cdf_{dataset}.png")
        plot_latency_cdf(arm_dir, x86_dir, output_file, dataset)
    
    # 4. Comparison Matrices for each platform
    print("\n[4/4] Dataset Comparison Matrices...")
    for platform in ["ARM", "x86"]:
        output_file = str(OUTPUT_DIR / f"comparison_matrix_{platform}.png")
        plot_dataset_comparison_matrix(platform, specialized_datasets, output_file)
    
    print("\n" + "=" * 70)
    print("✅ All visualizations generated successfully!")
    print(f"   Output directory: {OUTPUT_DIR}/")
    print("=" * 70 + "\n")
    
    # List generated files
    print("Generated files:")
    for f in sorted(OUTPUT_DIR.glob("*.png")):
        print(f"  • {f.name}")
    print()


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Advanced Visualization for Medical RAG Profiling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all visualizations
  python3 visualization_advanced.py --all
  
  # Generate specific type
  python3 visualization_advanced.py --type boxplot --dataset 100
  python3 visualization_advanced.py --type violin --platform ARM
  python3 visualization_advanced.py --type cdf --dataset 100
  python3 visualization_advanced.py --type matrix --platform ARM
  
  # Show percentile report only
  python3 visualization_advanced.py --report --dataset 100
        """
    )
    
    parser.add_argument('--all', action='store_true',
                        help='Generate all visualization types for all datasets')
    parser.add_argument('--type', choices=['boxplot', 'violin', 'cdf', 'matrix'],
                        help='Type of visualization to generate')
    parser.add_argument('--dataset', default='100',
                        help='Dataset name (100, cardio, infection, trauma)')
    parser.add_argument('--platform', default='ARM', choices=['ARM', 'x86'],
                        help='Platform for violin/matrix plots')
    parser.add_argument('--output', help='Custom output file path')
    parser.add_argument('--report', action='store_true',
                        help='Print percentile report to console')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Handle --all flag
    if args.all:
        generate_all_visualizations()
        return
    
    # Handle --report flag
    if args.report:
        print("\n" + "=" * 70)
        print("PERCENTILE REPORT")
        print("=" * 70)
        
        for platform in ["ARM", "x86"]:
            result_dir = RESULTS_DIR / f"{platform}_{args.dataset}"
            latencies = collect_latencies(str(result_dir))
            if latencies:
                pct = calculate_percentiles(latencies)
                print_percentiles_report(f"{platform}_{args.dataset}", pct)
        return
    
    # Handle specific visualization types
    if args.type == 'boxplot':
        arm_dir = str(RESULTS_DIR / f"ARM_{args.dataset}")
        x86_dir = str(RESULTS_DIR / f"x86_{args.dataset}")
        output_file = args.output or str(OUTPUT_DIR / f"boxplot_{args.dataset}.png")
        plot_latency_boxplot(arm_dir, x86_dir, output_file, args.dataset)
    
    elif args.type == 'violin':
        datasets = ["cardio", "infection", "trauma"]
        output_file = args.output or str(OUTPUT_DIR / f"violin_{args.platform}.png")
        plot_latency_violin_by_dataset(datasets, args.platform, output_file)
    
    elif args.type == 'cdf':
        arm_dir = str(RESULTS_DIR / f"ARM_{args.dataset}")
        x86_dir = str(RESULTS_DIR / f"x86_{args.dataset}")
        output_file = args.output or str(OUTPUT_DIR / f"cdf_{args.dataset}.png")
        plot_latency_cdf(arm_dir, x86_dir, output_file, args.dataset)
    
    elif args.type == 'matrix':
        datasets = ["cardio", "infection", "trauma"]
        output_file = args.output or str(OUTPUT_DIR / f"comparison_matrix_{args.platform}.png")
        plot_dataset_comparison_matrix(args.platform, datasets, output_file)
    
    else:
        # No specific action requested, show help
        parser.print_help()
        print("\n💡 Tip: Use --all to generate all visualizations at once!")


if __name__ == '__main__':
    main()

