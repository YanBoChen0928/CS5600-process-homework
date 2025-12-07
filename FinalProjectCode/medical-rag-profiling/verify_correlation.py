#!/usr/bin/env python3
"""
Verify correlation between query length and E-core utilization
for each medical domain dataset.
"""

import json
from pathlib import Path
from scipy import stats
import numpy as np

# Define paths
RESULTS_DIR = Path(__file__).parent / "results"

# E-cores for M2 Pro (8P+4E): cores 8-11
E_CORES = [8, 9, 10, 11]
P_CORES = [0, 1, 2, 3, 4, 5, 6, 7]

def analyze_dataset(dataset_name: str, result_dir: str):
    """Analyze correlation for a single dataset."""
    result_path = RESULTS_DIR / result_dir
    
    if not result_path.exists():
        print(f"  ❌ Directory not found: {result_path}")
        return None
    
    query_lengths = []
    e_core_utils = []
    latencies = []
    
    # Read all query JSON files
    for json_file in sorted(result_path.glob("query_*_run_*.json")):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if not data.get("success", False):
                continue
            
            # Get query length from metadata.query_text
            query = data.get("metadata", {}).get("query_text", "")
            query_len = len(query)
            
            # Get E-core utilization from per_core data
            per_core = data.get("cpu", {}).get("per_core", [])
            if len(per_core) >= 12:
                e_core_avg = np.mean([per_core[i] for i in E_CORES])
            else:
                continue
            
            # Get latency (total_ms -> convert to seconds)
            latency = data.get("latency", {}).get("total_ms", 0) / 1000.0
            
            query_lengths.append(query_len)
            e_core_utils.append(e_core_avg)
            latencies.append(latency)
            
        except Exception as e:
            continue
    
    if len(query_lengths) < 10:
        print(f"  ❌ Not enough data points: {len(query_lengths)}")
        return None
    
    # Calculate correlations
    # 1. Query Length vs E-core Utilization
    r_len_ecore, p_len_ecore = stats.pearsonr(query_lengths, e_core_utils)
    
    # 2. Latency vs E-core Utilization (bonus)
    r_lat_ecore, p_lat_ecore = stats.pearsonr(latencies, e_core_utils)
    
    return {
        "n": len(query_lengths),
        "r_length_ecore": r_len_ecore,
        "p_length_ecore": p_len_ecore,
        "r_latency_ecore": r_lat_ecore,
        "p_latency_ecore": p_lat_ecore,
        "query_len_range": (min(query_lengths), max(query_lengths)),
        "e_core_util_range": (min(e_core_utils), max(e_core_utils)),
    }

def main():
    print("=" * 70)
    print(" Correlation Analysis: Query Length vs E-core Utilization")
    print("=" * 70)
    print()
    
    datasets = [
        ("General (100)", "ARM_100"),
        ("Cardiology", "ARM_cardio"),
        ("Infection", "ARM_infection"),
        ("Trauma", "ARM_trauma"),
    ]
    
    results = {}
    
    for name, dir_name in datasets:
        print(f"📊 Analyzing {name}...")
        result = analyze_dataset(name, dir_name)
        if result:
            results[name] = result
            print(f"  ✓ n = {result['n']} data points")
            print(f"  ✓ Query length range: {result['query_len_range'][0]}-{result['query_len_range'][1]} chars")
            print(f"  ✓ E-core util range: {result['e_core_util_range'][0]:.2f}-{result['e_core_util_range'][1]:.2f}%")
        print()
    
    # Summary table
    print("=" * 70)
    print(" CORRELATION RESULTS: Query Length vs E-core Utilization")
    print("=" * 70)
    print()
    print(f"{'Dataset':<20} {'r':>10} {'p-value':>12} {'Significant':>12} {'n':>8}")
    print("-" * 70)
    
    for name, r in results.items():
        sig = "Yes (p<0.05)" if r['p_length_ecore'] < 0.05 else "No"
        if r['p_length_ecore'] < 0.001:
            sig = "Yes (p<0.001)"
        print(f"{name:<20} {r['r_length_ecore']:>10.4f} {r['p_length_ecore']:>12.4f} {sig:>12} {r['n']:>8}")
    
    print()
    print("=" * 70)
    print(" BONUS: Latency vs E-core Utilization")
    print("=" * 70)
    print()
    print(f"{'Dataset':<20} {'r':>10} {'p-value':>12} {'Significant':>12}")
    print("-" * 70)
    
    for name, r in results.items():
        sig = "Yes (p<0.05)" if r['p_latency_ecore'] < 0.05 else "No"
        if r['p_latency_ecore'] < 0.001:
            sig = "Yes (p<0.001)"
        print(f"{name:<20} {r['r_latency_ecore']:>10.4f} {r['p_latency_ecore']:>12.4f} {sig:>12}")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
