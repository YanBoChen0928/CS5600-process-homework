# Performance Comparison: ARM vs x86 (infection)

**Date:** 2025-11-20  
**Dataset:** infection  
**ARM Data Points:** 155  
**x86 Data Points:** 155

---

## Summary Statistics

| Metric                     | ARM M2 Pro | x86 + RTX 4090 | Speedup (x86/ARM) |
|---------------------------|------------|----------------|-------------------|
| **Latency (Median)**      | 9.95s | 2.14s | 4.65× |
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
- x86 shows lower latency variance (0.39s vs 2.01s std dev)

### CPU Utilization
- ARM: ~7.6 cores actively used on average
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
- Memory capacity is limited

### Use x86 + RTX 4090 when:
- Low latency is critical (e.g., real-time systems)
- High throughput requirements
- GPU resources are available
- Budget allows for higher-end hardware
