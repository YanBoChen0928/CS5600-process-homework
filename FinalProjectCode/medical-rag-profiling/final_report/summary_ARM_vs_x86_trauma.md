# Performance Comparison: ARM vs x86 (trauma)

**Date:** 2025-11-20  
**Dataset:** trauma  
**ARM Data Points:** 110  
**x86 Data Points:** 110

---

## Summary Statistics

| Metric                     | ARM M2 Pro | x86 + RTX 4090 | Speedup (x86/ARM) |
|---------------------------|------------|----------------|-------------------|
| **Latency (Median)**      | 10.41s | 2.36s | 4.41× |
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
- x86 shows lower latency variance (0.41s vs 2.41s std dev)

### CPU Utilization
- ARM: ~7.5 cores actively used on average
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
- Memory capacity is limited

### Use x86 + RTX 4090 when:
- Low latency is critical (e.g., real-time systems)
- High throughput requirements
- GPU resources are available
- Budget allows for higher-end hardware
