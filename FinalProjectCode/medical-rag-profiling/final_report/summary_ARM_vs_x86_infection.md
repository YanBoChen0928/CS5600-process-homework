# Performance Comparison: ARM vs x86 (infection)

**Date:** 2025-11-22  
**Dataset:** infection  
**ARM Data Points:** 155  
**x86 Data Points:** 155

---

## Summary Statistics

| Metric                     | ARM M2 Pro | x86 + RTX 4090 | Speedup (x86/ARM) |
|---------------------------|------------|----------------|-------------------|
| **Latency (Min)**         | 4.89s | 0.80s | - |
| **Latency (p25)**         | 8.82s | 1.88s | - |
| **Latency (Median/p50)**  | 9.95s | 2.14s | 4.65× |
| **Latency (p75)**         | 11.09s | 2.37s | - |
| **Latency (p95)** ⭐      | 13.60s | 2.85s | 4.77× |
| **Latency (p99)** ⭐      | 14.91s | 3.01s | 4.96× |
| **Latency (Max)**         | 17.60s | 3.08s | - |
| **Latency (Mean)**        | 10.01s | 2.15s | 4.66× |
| **Latency (Std Dev)**     | 2.01s | 0.39s | - |
| **CPU Peak (Total %)**    | 866.9% | 111.4% | - |
| **CPU Average (Total %)** | 755.0% | 73.1% | - |
| **Memory Peak (GB)**      | 8.00 | 1.97 | - |
| **Cores Used (Avg)**      | 7.6 | 0.7 | - |

---

## Key Findings

### Performance
- **x86 + RTX 4090 is 4.65× faster** than ARM M2 Pro (median latency)
- **Tail latency (p95):** ARM 13.60s vs x86 2.85s (4.77× difference)
- **Worst-case (p99):** ARM 14.91s vs x86 3.01s (4.96× difference)
- x86 shows lower latency variance (0.39s vs 2.01s std dev)

### CPU Utilization
- ARM: ~7.6 cores actively used on average
  - **P-cores (Performance)**: 10.31% avg utilization, 97.9% of workload
  - **E-cores (Efficiency)**: 0.22% avg utilization, 2.1% of workload
- x86: ~0.7 cores actively used on average
- x86 exhibits lower parallelization efficiency

### Memory Footprint
- ARM: 8.00 GB average (unified memory)
- x86: 1.97 GB average (discrete memory)
- ARM shows 307% higher memory usage

---

## Deployment Recommendations

### Use ARM M2 Pro when:
- Budget-constrained environments
- Edge deployment scenarios
- Power efficiency is critical
- Moderate latency requirements (p95 < 13.6s acceptable)

### Use x86 + RTX 4090 when:
- Low latency is critical (p95 < 2.9s required)
- Strict tail latency requirements (p99 < 3.0s)
- High throughput requirements
- GPU resources are available
- Budget allows for higher-end hardware
