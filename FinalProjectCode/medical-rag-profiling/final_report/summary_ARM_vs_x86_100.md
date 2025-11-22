# Performance Comparison: ARM vs x86 (100)

**Date:** 2025-11-20  
**Dataset:** 100  
**ARM Data Points:** 500  
**x86 Data Points:** 500

---

## Summary Statistics

| Metric                     | ARM M2 Pro | x86 + RTX 4090 | Speedup (x86/ARM) |
|---------------------------|------------|----------------|-------------------|
| **Latency (Median)**      | 10.60s | 2.30s | 4.62× |
| **Latency (Mean)**        | 10.78s | 2.31s | 4.68× |
| **Latency (Std Dev)**     | 2.38s | 0.42s | - |
| **CPU Peak (Total %)**    | 862.8% | 111.1% | - |
| **CPU Average (Total %)** | 759.9% | 76.1% | - |
| **Memory Peak (GB)**      | 8.02 | 2.02 | - |
| **Cores Used (Avg)**      | 7.6 | 0.8 | - |

---

## Key Findings

### Performance
- **x86 + RTX 4090 is 4.62× faster** than ARM M2 Pro (median latency)
- x86 shows lower latency variance (0.42s vs 2.38s std dev)

### CPU Utilization
- ARM: ~7.6 cores actively used on average
- x86: ~0.8 cores actively used on average
- x86 exhibits lower parallelization efficiency

### Memory Footprint
- ARM: 8.02 GB average (unified memory)
- x86: 2.02 GB average (discrete memory)
- ARM shows 296% higher memory usage

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
