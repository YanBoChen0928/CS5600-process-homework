#!/usr/bin/env python3
"""
Recalculate P-cores vs E-cores statistics with corrected core classification
M2 Pro 12-core: Cores 0-7 are P-cores, Cores 8-11 are E-cores
"""

import json
import glob
import numpy as np

# Correct core classification for M2 Pro 12-core
P_CORES = list(range(0, 8))  # 0-7 (8 cores)
E_CORES = list(range(8, 12))  # 8-11 (4 cores)

datasets = ['100', 'cardio', 'infection', 'trauma']

print("=" * 80)
print(" RECALCULATED P-cores vs E-cores Analysis (Corrected: 8P+4E)".center(80))
print("=" * 80)
print()

for dataset in datasets:
    result_dir = f'results/ARM_{dataset}'
    
    p_cores_list = []
    e_cores_list = []
    
    for f in sorted(glob.glob(f'{result_dir}/query_*_run_*.json')):
        try:
            with open(f) as file:
                data = json.load(file)
                if not data.get('success'):
                    continue
                
                # Get per_core data from CPU section
                per_core = data['cpu'].get('per_core', [])
                
                if len(per_core) >= 12:
                    # Recalculate with correct classification
                    p_cores_avg = np.mean([per_core[i] for i in P_CORES])
                    e_cores_avg = np.mean([per_core[i] for i in E_CORES])
                    
                    p_cores_list.append(p_cores_avg)
                    e_cores_list.append(e_cores_avg)
        except Exception as e:
            print(f"Warning: {f}: {e}")
            continue
    
    if not p_cores_list:
        print(f"### {dataset.upper()} ###")
        print("  No data found")
        continue
    
    # Calculate statistics
    p_mean = np.mean(p_cores_list)
    e_mean = np.mean(e_cores_list)
    total = p_mean + e_mean
    
    p_workload_pct = (p_mean / total * 100) if total > 0 else 0
    e_workload_pct = (e_mean / total * 100) if total > 0 else 0
    
    print(f"### {dataset.upper()} ###")
    print(f"  Samples: {len(p_cores_list)}")
    print(f"  P-cores (0-7) Average: {p_mean:.2f}%")
    print(f"  E-cores (8-11) Average: {e_mean:.2f}%")
    print(f"  Workload Distribution:")
    print(f"    P-cores handle: {p_workload_pct:.1f}% of workload")
    print(f"    E-cores handle: {e_workload_pct:.1f}% of workload")
    print()

print("=" * 80)
print(" Comparison with Previous (Incorrect) Classification".center(80))
print("=" * 80)
print()
print("Previous (6P+6E):  P-cores 98.5%, E-cores 1.5%")
print("Corrected (8P+4E): P-cores ???%, E-cores ???%")
print()
print("Run this script to see corrected values!")
print("=" * 80)
