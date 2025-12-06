# Performance Comparison: ARM vs x86 (trauma)

**Date:** 2025-11-22  
**Dataset:** trauma  
**ARM Data Points:** 110  
**x86 Data Points:** 110

---

## Summary Statistics

| Metric                     | ARM M2 Pro | x86 + RTX 4090 | Speedup (x86/ARM) |
|---------------------------|------------|----------------|-------------------|
| **Latency (Min)**         | 5.84s | 1.37s | - |
| **Latency (p25)**         | 9.33s | 2.05s | - |
| **Latency (Median/p50)**  | 10.41s | 2.36s | 4.41× |
| **Latency (p75)**         | 12.19s | 2.61s | - |
| **Latency (p95)** ⭐      | 14.75s | 3.08s | 4.79× |
| **Latency (p99)** ⭐      | 16.33s | 3.42s | 4.78× |
| **Latency (Max)**         | 20.24s | 3.48s | - |
| **Latency (Mean)**        | 10.92s | 2.35s | 4.64× |
| **Latency (Std Dev)**     | 2.41s | 0.41s | - |
| **CPU Peak (Total %)**    | 858.6% | 111.2% | - |
| **CPU Average (Total %)** | 752.9% | 76.8% | - |
| **Memory Peak (GB)**      | 8.09 | 2.00 | - |
| **Cores Used (Avg)**      | 7.5 | 0.8 | - |

---

## Key Findings

### Performance
- **x86 + RTX 4090 is 4.41× faster** than ARM M2 Pro (median latency)
- **Tail latency (p95):** ARM 14.75s vs x86 3.08s (4.79× difference)
- **Worst-case (p99):** ARM 16.33s vs x86 3.42s (4.78× difference)
- x86 shows lower latency variance (0.41s vs 2.41s std dev)

### CPU Utilization
- ARM: ~7.5 cores actively used on average
  - **P-cores (Performance)**: 9.03% avg utilization, 96.2% of workload
  - **E-cores (Efficiency)**: 0.36% avg utilization, 3.8% of workload
- x86: ~0.8 cores actively used on average
- x86 exhibits lower parallelization efficiency

### Memory Footprint
- ARM: 8.09 GB average (unified memory)
- x86: 2.00 GB average (discrete memory)
- ARM shows 304% higher memory usage

---

## Deployment Recommendations

### Use ARM M2 Pro when:
- Budget-constrained environments
- Edge deployment scenarios
- Power efficiency is critical
- Moderate latency requirements (p95 < 14.7s acceptable)

### Use x86 + RTX 4090 when:
- Low latency is critical (p95 < 3.1s required)
- Strict tail latency requirements (p99 < 3.4s)
- High throughput requirements
- GPU resources are available
- Budget allows for higher-end hardware
