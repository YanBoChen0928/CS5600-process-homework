# System Design Overview

**Project:** Medical RAG Workload Characterization  
**Author:** Yan-Bo Chen  
**Date:** November 21, 2025

---

## Architecture Overview

This project characterizes the performance of a Medical RAG (Retrieval-Augmented Generation) system across two hardware configurations:

### Configuration 1: ARM CPU-Only
- **Hardware:** Apple MacBook Pro M2 Pro
- **CPU:** 12 cores (6 Performance + 6 Efficiency)
- **Memory:** 16GB unified memory
- **Runtime:** Ollama with Llama 3.2:3B (CPU-only mode)

### Configuration 2: x86 + GPU
- **Hardware:** Intel i9 + NVIDIA RTX 4090
- **CPU:** 32 cores
- **GPU:** RTX 4090 (24GB VRAM)
- **Memory:** 64GB DDR4
- **Runtime:** Ollama with Llama 3.2:3B (GPU-accelerated)

---

## System Components

### 1. RAG Pipeline
- **Query Processing:** Medical condition extraction
- **Retrieval:** Dual-index vector search
- **Generation:** LLM-based response synthesis
- **Validation:** Medical query filtering

### 2. Profiling System
- **CPU Monitoring:** Per-core and total utilization
- **Memory Tracking:** Used, available, peak
- **Latency Measurement:** Retrieval, generation, total
- **Timeline Recording:** 500ms sampling interval

### 3. CLI Tool (medrag.py)
- **run:** Execute single experiment
- **batch:** Run multiple experiments
- **analyze:** Generate statistics
- **visualize:** Create charts
- **compare:** ARM vs x86 comparison
- **report:** Generate reports
- **latex:** Create LaTeX tables

---

## Data Flow

```
Medical Query Input
        │
        ▼
Condition Extraction (LLM)
        │
        ▼
Vector Retrieval (Dual-Index)
        │
        ▼
Response Generation (LLM)
        │
        ▼
Clinical Guidance Output
        │
        ▼
Performance Metrics (JSON)
```

---

## Performance Metrics

### Primary Metrics
- **Latency:** Total query response time
- **CPU Utilization:** Per-core and aggregate
- **Memory Footprint:** Used and peak
- **Timeline:** Resource usage over time

### Secondary Metrics
- **Retrieval Time:** Vector search latency
- **Generation Time:** LLM inference latency
- **Overhead:** Pipeline processing time

---

## Experimental Design

### Test Datasets
- 10, 25, 100 general medical queries
- Category-specific: cardio, infection, trauma
- Each query × 5 runs for statistical significance

### Output Structure
```
results/
├── ARM_<dataset>/
│   ├── query_*.json      # Performance data
│   └── system_info.json  # Platform info
└── x86_<dataset>/
    ├── query_*.json
    └── system_info.json
```

### Analysis Output
```
final_report/
├── comparison_*.png      # Visual comparisons
├── summary_*.md          # Markdown reports
├── summary_*.csv         # Data tables
└── table_*.tex           # LaTeX tables
```

---

## Key Design Decisions

### 1. CPU-Only ARM Configuration
**Rationale:** Edge deployment scenarios require CPU-only execution
- Forces ARM to use all CPU resources
- Realistic edge/mobile deployment
- Tests CPU efficiency vs GPU acceleration

### 2. Dual-Platform Comparison
**Rationale:** Informs deployment trade-offs
- ARM: Edge deployment, lower power
- x86 + GPU: Cloud deployment, higher performance

### 3. Medical RAG Workload
**Rationale:** Representative AI workload
- Compute-intensive (LLM inference)
- Memory-intensive (vector search)
- Real-world application

---

## Future Extensions

### Potential Improvements
1. **Power Efficiency Analysis**
   - Measure power consumption
   - Calculate performance-per-watt

2. **Quantization Impact**
   - Test INT8/INT4 quantization
   - Compare accuracy vs performance

3. **Batch Inference**
   - Test throughput vs latency
   - Evaluate GPU batch efficiency

4. **Multi-GPU Scaling**
   - Test with multiple GPUs
   - Measure scaling efficiency

---

## Related Documentation

- Main README: ../README.md
- ARM Setup: ARM_SETUP.md
- x86 Setup: X86_SETUP.md
- CLI Reference: CLI_REFERENCE.md
- Analysis Guide: ANALYSIS_GUIDE.md
