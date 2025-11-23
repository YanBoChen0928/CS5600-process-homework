# Performance Comparison: ARM vs x86 (cardio)

**Date:** 2025-11-22  
**Dataset:** cardio  
**ARM Data Points:** 135  
**x86 Data Points:** 135

---

## Summary Statistics

| Metric                     | ARM M2 Pro | x86 + RTX 4090 | Speedup (x86/ARM) |
|---------------------------|------------|----------------|-------------------|
| **Latency (Min)**         | 5.66s | 1.06s | - |
| **Latency (p25)**         | 10.28s | 2.03s | - |
| **Latency (Median/p50)**  | 12.03s | 2.32s | 5.19× |
| **Latency (p75)**         | 14.14s | 2.62s | - |
| **Latency (p95)** ⭐      | 17.84s | 3.02s | 5.90× |
| **Latency (p99)** ⭐      | 22.80s | 3.27s | 6.97× |
| **Latency (Max)**         | 23.52s | 5.30s | - |
| **Latency (Mean)**        | 12.39s | 2.34s | 5.30× |
| **Latency (Std Dev)**     | 3.20s | 0.51s | - |
| **CPU Peak (Total %)**    | 924.0% | 113.9% | - |
| **CPU Average (Total %)** | 779.5% | 77.1% | - |
| **Memory Peak (GB)**      | 7.77 | 1.89 | - |
| **Cores Used (Avg)**      | 7.8 | 0.8 | - |

---

## Key Findings

### Performance
- **x86 + RTX 4090 is 5.19× faster** than ARM M2 Pro (median latency)
- **Tail latency (p95):** ARM 17.84s vs x86 3.02s (5.90× difference)
- **Worst-case (p99):** ARM 22.80s vs x86 3.27s (6.97× difference)
- x86 shows lower latency variance (0.51s vs 3.20s std dev)

### CPU Utilization
- ARM: ~7.8 cores actively used on average
- x86: ~0.8 cores actively used on average
- x86 exhibits lower parallelization efficiency

### Memory Footprint
- ARM: 7.77 GB average (unified memory)
- x86: 1.89 GB average (discrete memory)
- ARM shows 311% higher memory usage

---

## Deployment Recommendations

### Use ARM M2 Pro when:
- Budget-constrained environments
- Edge deployment scenarios
- Power efficiency is critical
- Moderate latency requirements (p95 < 17.8s acceptable)

### Use x86 + RTX 4090 when:
- Low latency is critical (p95 < 3.0s required)
- Strict tail latency requirements (p99 < 3.3s)
- High throughput requirements
- GPU resources are available
- Budget allows for higher-end hardware
