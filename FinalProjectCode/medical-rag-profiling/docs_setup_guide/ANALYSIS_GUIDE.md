# Data Analysis Guide: ARM vs x86 Performance Comparison

**Project:** Medical RAG Workload Characterization  
**Author:** Yan-Bo Chen  
**Date:** November 21, 2025  
**Purpose:** Analysis methodology and visualization guide for ARM (M2 Pro) and x86 + RTX 4090 performance data

---

## Table of Contents

1. [Experiment Data Structure](#experiment-data-structure)
2. [Analysis Workflow Overview](#analysis-workflow-overview)
3. [Single-Platform Analysis](#single-platform-analysis)
4. [Cross-Platform Comparison](#cross-platform-comparison)
5. [Final Report Generation](#final-report-generation)
6. [LaTeX Table Generation](#latex-table-generation)
7. [Troubleshooting](#troubleshooting)

---

## Experiment Data Structure

### Expected Directory Structure

After experiments complete, you will have:

```
medical-rag-profiling/
├── results/
│   ├── ARM_25/                    # ARM platform - 25 queries × 5 runs
│   │   ├── query_000_run_00.json
│   │   ├── query_000_run_01.json
│   │   ├── ...
│   │   ├── system_info.json
│   │   └── experiment_log.txt
│   │
│   ├── ARM_100/                   # ARM platform - 100 queries × 5 runs
│   ├── ARM_cardio/                # ARM platform - Cardio category
│   ├── ARM_infection/             # ARM platform - Infection category
│   ├── ARM_trauma/                # ARM platform - Trauma category
│   │
│   ├── x86_25/                    # x86 platform - 25 queries × 5 runs
│   ├── x86_100/                   # x86 platform - 100 queries × 5 runs
│   ├── x86_cardio/                # x86 platform - Cardio category
│   ├── x86_infection/             # x86 platform - Infection category
│   └── x86_trauma/                # x86 platform - Trauma category
│
└── final_report/                  # Analysis output
    ├── summary_100.md             # Markdown summary
    ├── summary_100.csv            # CSV data
    ├── table_100.tex              # LaTeX table
    └── comparison_ARM_vs_x86_100.png
```

### JSON Data Format (Per Query)

```json
{
  "metadata": {
    "query_id": 0,
    "run_id": 0,
    "timestamp": "2025-11-21T12:34:56",
    "query_text": "What are the symptoms of hypertension?",
    "success": true,
    "error": null
  },
  
  "latency": {
    "total_ms": 12345.67,
    "retrieval_ms": 123.45,
    "generation_ms": 12000.12,
    "overhead_ms": 222.10
  },
  
  "cpu": {
    "peak_percent": 875.3,
    "average_percent": 543.2,
    "per_core": [85.2, 78.3, 65.1, ...]
  },
  
  "memory": {
    "used_gb": 3.45,
    "percent": 21.5,
    "available_gb": 12.55
  },
  
  "timeline": [
    {"t": 0.0, "cpu_total": 234.5, "cpu_cores": [...], "mem_gb": 3.2},
    {"t": 0.5, "cpu_total": 567.8, "cpu_cores": [...], "mem_gb": 3.4},
    ...
  ],
  
  "timeline_summary": {
    "cpu_peak_from_timeline": 890.5,
    "cpu_avg_from_timeline": 550.2,
    "memory_peak_from_timeline": 3.5,
    "num_samples": 45
  }
}
```

---

## Analysis Workflow Overview

### Complete Analysis Pipeline (Experiment to Paper)

```
Step 1: Run experiments on ARM
    ./medrag.py batch --all
    
Step 2: Run experiments on x86
    ./medrag.py batch --all
    
Step 3: Single-platform analysis
    ./medrag.py analyze --output results/ARM_100
    ./medrag.py visualize --output results/ARM_100
    
Step 4: Cross-platform comparison
    ./medrag.py compare --dataset 100
    ./medrag.py compare --all
    
Step 5: Generate reports
    ./medrag.py report --dataset 100
    ./medrag.py report --all
    
Step 6: Generate LaTeX tables
    ./medrag.py latex --dataset 100
    ./medrag.py latex --all
```

---

## Single-Platform Analysis

### Run Analysis Script

```bash
./medrag.py analyze --output results/ARM_100
```

**Output includes:**
- Latency statistics (min, max, median, mean, std dev)
- CPU utilization (peak, average)
- Per-core CPU usage
- Memory usage statistics
- Response quality metrics
- Timeline sampling statistics

### Generate Visualizations

```bash
./medrag.py visualize --output results/ARM_100
```

**Generated files:**

1. **cpu_heatmap.png** — CPU core utilization heatmap
   - Per-core usage over time
   - ARM: Distinguishes P-cores vs E-cores
   - x86: All cores displayed equally

2. **latency_distribution.png** — Latency histogram
   - Query response time distribution
   - Marks mean and median

3. **memory_timeline.png** — Memory usage timeline
   - Tracks memory across queries
   - Detects memory leaks

4. **core_utilization_comparison.png** — Core usage comparison
   - ARM: P-cores vs E-cores
   - x86: All cores

5. **cpu_timeline_aggregate.png** — Aggregated CPU timeline
   - Overlays all query CPU traces
   - Red line = average

---

## Cross-Platform Comparison

### Compare Specific Dataset

```bash
./medrag.py compare --dataset 100
```

**Automatically finds and compares:**
- `results/ARM_100/` vs `results/x86_100/`

### Compare All Datasets

```bash
./medrag.py compare --all
```

**Generated files (saved in final_report/):**

**comparison_ARM_vs_x86_<dataset>.png** — Multi-panel comparison
- Panel 1: Latency distribution (box plots)
- Panel 2: CPU peak utilization (bar chart)
- Panel 3: CPU average utilization (bar chart)
- Panel 4: Memory footprint (bar chart)

### Interpreting Results

**Latency Comparison:**
```
If ARM median = 12.3s, x86 median = 8.5s
→ Speedup = 12.3 / 8.5 = 1.45×
→ "x86 is 1.45× faster than ARM"
```

**CPU Comparison:**
```
ARM: Peak = 890%, Average = 543%
x86: Peak = 1200%, Average = 785%

ARM uses ~5.4 cores (543% ÷ 100%)
x86 uses ~7.9 cores (785% ÷ 100%)
```

---

## Final Report Generation

### Generate Markdown and CSV Reports

```bash
./medrag.py report --dataset 100
```

**Output files:**
- `final_report/summary_ARM_vs_x86_100.md` — Markdown summary
- `final_report/summary_ARM_vs_x86_100.csv` — CSV data (Excel-compatible)

### Markdown Report Example

```markdown
# Performance Comparison: ARM vs x86 (100 Queries)

## Summary Statistics

| Metric                     | ARM M2 Pro | x86 + RTX 4090 | Speedup |
|---------------------------|------------|----------------|---------|
| **Latency (Median)**      | 12.34s     | 8.56s          | 1.44×   |
| **CPU Peak (Total %)**    | 890.2%     | 1245.6%        | -       |
| **Memory Peak (GB)**      | 3.58       | 4.52           | -       |

## Key Findings

- x86 + RTX 4090 is **1.44× faster** than ARM M2 Pro
- ARM shows 20% lower memory usage
```

---

## LaTeX Table Generation

### Generate LaTeX Tables

```bash
./medrag.py latex --dataset 100
```

**Output file:** `final_report/table_100.tex`

### LaTeX Table Example

```latex
\begin{table}[htbp]
\centering
\caption{Performance Comparison: ARM M2 Pro vs x86 + RTX 4090}
\label{tab:perf_comparison_100}
\begin{tabular}{lrrr}
\toprule
\textbf{Metric} & \textbf{ARM} & \textbf{x86} & \textbf{Speedup} \\
\midrule
Latency (Median) & 12.34s & 8.56s & 1.44× \\
CPU Peak (\%)    & 890.2  & 1245.6 & - \\
\bottomrule
\end{tabular}
\end{table}
```

### Usage in LaTeX Paper

```latex
% In preamble
\usepackage{booktabs}

% In document
\input{final_report/table_100.tex}
```

---

## Troubleshooting

### Issue 1: Missing Data Files

**Problem:** Some query JSON files are missing or corrupted

**Solution:**
```bash
# Check data integrity
python -c "
import glob, json
files = glob.glob('results/ARM_100/query_*.json')
print(f'Total files: {len(files)}')
for f in files:
    try:
        json.load(open(f))
    except:
        print(f'Corrupted: {f}')
"
```

### Issue 2: Compare Command Fails

**Problem:** Missing ARM or x86 data

**Solution:**
```bash
# Check which directories exist
ls results/

# Verify data was transferred correctly
ls results/x86_100/query_*.json | wc -l
```

### Issue 3: Incomplete Data Transfer

**Problem:** Partial file transfer

**Solution:**
```bash
# Verify archive integrity
tar -tzf x86_results.tar.gz | wc -l

# Check disk space
df -h

# Use checksum for verification
sha256sum x86_results.tar.gz > x86_results.sha256
sha256sum -c x86_results.sha256
```

---

## Paper Writing Guidelines

### Results Section Structure

```markdown
## 5. Results

### 5.1 Performance Characterization

#### 5.1.1 ARM M2 Pro Performance
- Median latency: 12.34s
- CPU usage: Average 5.4 cores
- Memory: 3.4 GB
- Reference: cpu_heatmap.png, latency_distribution.png

#### 5.1.2 x86 + RTX 4090 Performance
- Median latency: 8.56s
- CPU usage: Average 7.9 cores
- Memory: 4.2 GB

### 5.2 Comparative Analysis
- x86 achieves 1.44× speedup
- Reference: comparison_ARM_vs_x86_100.png
- Reference: table_100.tex
```

---

## Analysis Checklist

Before finalizing your analysis:

### Data Completeness
- [ ] ARM data collection complete
- [ ] x86 data collection complete
- [ ] No corrupted JSON files
- [ ] system_info.json files exist

### Single-Platform Analysis
- [ ] ARM analyze and visualize complete
- [ ] x86 analyze and visualize complete
- [ ] All charts generated

### Cross-Platform Comparison
- [ ] All comparison charts generated
- [ ] Charts are clear and readable
- [ ] Data trends match expectations

### Report Generation
- [ ] Markdown reports generated
- [ ] CSV reports generated
- [ ] LaTeX tables generated
- [ ] All files in final_report directory

### Paper Preparation
- [ ] Selected best charts for paper
- [ ] Chart resolution ≥ 300 DPI
- [ ] LaTeX table format correct
- [ ] Statistical significance verified

---

**For complete CLI reference, see CLI_REFERENCE.md**

**For platform-specific setup, see ARM_SETUP.md and X86_SETUP.md**
